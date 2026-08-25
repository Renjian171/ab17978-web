#!/bin/bash
# =============================================================================
#  Ab17978 容器启动入口
#  - 激活 conda 环境、跑 Django migrate（建 Django 内置表）
#  - 业务表 managed=False，migrate 不建；用 sqlite_schema.sql 建四张业务表
#    （sequences/promoters/operons/srna_structures），随后 loaddata 导数据
#  - 按 DEPLOY_MODE 选择 web 服务进程，并用 exec 让它成为 PID1：
#      cluster    : httpd -DFOREGROUND（mod_wsgi 托管 Django，子路径 /ab17978）
#      standalone : waitress 直接服务 :80（独立 VM，根路径）
#  配合 docker run --restart=always，进程挂掉 / 宿主重启后容器自动拉起，
#  实现「宕机自愈」——区别于 13 节点其余要手动 docker exec 拉起的容器
#  （见《CBI Web 上线手册》§06：central_port 宕机 32h 的根因即 PID1=bash
#   + RestartPolicy=no + httpd 非 PID1）。
#
#  数据库：SQLite，文件放 /home/rjtian/ab17978-data/db.sqlite3
#    （独立于代码目录，git pull 不冲突，db 跨代码更新持久化）。
#    entrypoint 以 root 运行，负责建数据目录 + 放宽权限，让 httpd 守护进程
#    （容器内 apache 用户）可写 db 及其 -wal/-shm。
#
#  生产 settings：镜像 ENV DJANGO_SETTINGS_MODULE=myweb.settings_prod
#    （必须放 Dockerfile ENV，否则 docker exec 的 loaddata 读不到，会回退到
#     dev 的 MySQL settings。entrypoint 这里不再 export。）
# =============================================================================
set -e

# 1) 激活 conda 环境
source /opt/mambaforge/etc/profile.d/conda.sh
conda activate ab17978

# 2) 进入挂载进来的代码目录
#    宿主机 -v /home/rjtian:/home/rjtian，代码在 /home/rjtian/ab17978-web
cd /home/rjtian/ab17978-web || { echo "代码目录不存在: /home/rjtian/ab17978-web"; exit 1; }

# 3) SQLite 数据目录与权限
#    settings_prod.py 把 db 放在 /home/rjtian/ab17978-data/db.sqlite3。
#    该目录必须对 httpd 守护进程（容器内 apache，uid 48）可写——SQLite 写
#    db 时会在同目录建 -wal / -shm 文件，故目录而非仅文件要可写。
#    entrypoint 是 root，建目录并 chmod 777（数据目录只放一个 sqlite 文件，
#    放宽权限风险可控）。
DATA_DIR=/home/rjtian/ab17978-data
mkdir -p "$DATA_DIR"
chmod 777 "$DATA_DIR"

# 4) 幂等建表
#    migrate 建 Django 内置表（auth/admin/sessions/contenttypes 等）。
#    业务表 managed=False（migrate 不建），用镜像内 /sqlite_schema.sql 建（幂等）。
#    用 conda env 的 python（即 DJANGO_SETTINGS_MODULE=settings_prod）。
python manage.py migrate --no-input

# 业务表 schema：直接读镜像内的 /sqlite_schema.sql，幂等执行
if [ -f /sqlite_schema.sql ]; then
  python manage.py shell -c "
import sqlite3
from django.conf import settings
db = settings.DATABASES['default']['NAME']
sql = open('/sqlite_schema.sql').read()
conn = sqlite3.connect(db)
conn.executescript(sql)
conn.commit(); conn.close()
print('sqlite_schema applied to', db)
"
fi

# 5) 放宽 db 文件权限（migrate 以 root 建的文件归 root，httpd 的 apache 要写）
DBFILE="$DATA_DIR/db.sqlite3"
if [ -f "$DBFILE" ]; then
  chmod 666 "$DBFILE"
  # 可能存在的 WAL/共享内存文件一并放宽
  for ext in wal shm journal; do
    [ -f "$DBFILE-$ext" ] && chmod 666 "$DBFILE-$ext"
  done
fi

# 6) 按 DEPLOY_MODE 起 web 进程（exec → 成为 PID1）
case "${DEPLOY_MODE:-standalone}" in
  cluster)
    # 13 节点：httpd 前台运行，mod_wsgi 托管 Django（子路径 /ab17978）
    exec /usr/sbin/httpd -DFOREGROUND
    ;;
  standalone|*)
    # 独立 VM：waitress 直接服务 :80
    exec python -m waitress --listen=0.0.0.0:80 myweb.wsgi:application
    ;;
esac
