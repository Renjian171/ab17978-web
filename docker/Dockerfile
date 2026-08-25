# syntax=docker/dockerfile:1
# =============================================================================
#  Ab17978 数据库网站 — 容器镜像
#  一份镜像同时支持两种部署：
#    - cluster     : 13 节点 cbi.gxu.edu.cn，子路径 /ab17978，httpd+mod_wsgi 当 PID1
#    - standalone  : 独立 VM，根路径 /，waitress 直接服务 :80
#  由启动时的环境变量 DEPLOY_MODE 决定（见 entrypoint.sh）。
#
#  基础镜像：集群内用课题组定制镜像（已配好镜像源/时区/常用工具）；
#           集群外构建把下一行换成  FROM rockylinux:9
#
#  数据库：SQLite（容器内本地文件，持久化在 /home/rjtian/ab17978-data）。
#    13 节点共享 MariaDB 的 mysql.proc 系统表索引损坏，建库会触发
#    ERROR 1034，故改用 SQLite。业务数据 ~3MB，SQLite 完全够用。
#
#  生产 settings：rjtian 在仓库放 myweb/settings_prod.py，本镜像固定
#    ENV DJANGO_SETTINGS_MODULE=myweb.settings_prod —— 容器内 manage.py、
#    mod_wsgi、docker exec 的 loaddata 都统一读它。
# =============================================================================
FROM yhshao/rockylinux:9.3_v2.1

# 设置中国时区（基础镜像多半已设，幂等再设一次）
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
 && echo "Asia/Shanghai" > /etc/timezone

# -----------------------------------------------------------------------------
# 1) 系统依赖
#    - 编译工具链 + mod_wsgi/httpd 依赖：gcc make pcre-devel expat-devel
#    - python/mambaforge 安装依赖：openssl/libffi/bzip2/ncurses/sqlite 等 -devel
#    - sqlite-devel：Python 的 sqlite3 扩展 + Django sqlite 后端依赖
#    - wget/git/which：拉取 miniforge / mod_wsgi 源码
# -----------------------------------------------------------------------------
RUN dnf install -y epel-release \
 && dnf install -y \
      gcc gcc-c++ make wget tar git which \
      openssl-devel libffi-devel bzip2-devel ncurses-devel \
      gdbm-devel sqlite-devel tk-devel readline-devel \
      libuuid-devel libnsl2-devel \
      httpd httpd-devel pcre pcre-devel expat expat-devel \
 && dnf clean all

# -----------------------------------------------------------------------------
# 2) Miniforge：Python 3.12 + BLAST + primer3-py
#    延续「无 root 部署指南第四部分」的 conda 思路，装进 /opt/mambaforge。
#    blast 走 bioconda，primer3-py 走 conda-forge（避开 pip 编译失败）。
# -----------------------------------------------------------------------------
RUN curl -fsSL -o /tmp/mambaforge.sh \
      https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
 && bash /tmp/mambaforge.sh -b -p /opt/mambaforge && rm -f /tmp/mambaforge.sh
# PATH 优先指向 ab17978 环境：entrypoint、mod_wsgi 子进程、docker exec 的
# `python`/`blastp` 都直接解析到环境内（否则 docker exec 跑 loaddata 会用到系统
# python、找不到 Django）。
ENV PATH=/opt/mambaforge/envs/ab17978/bin:/opt/mambaforge/bin:$PATH
RUN mamba create -n ab17978 python=3.12 -y \
 && mamba install -n ab17978 -c bioconda blast -y \
 && mamba install -n ab17978 -c conda-forge primer3-py -y \
 && mamba clean -afy

# -----------------------------------------------------------------------------
# 3) Python 依赖
#    requirements-server.txt 由仓库提供（含 Django/DRF/biopython/waitress/
#    whitenoise/gunicorn 等）。SQLite 用 Django 自带后端，无需额外驱动。
#    （原仓库 requirements-server.txt 的 Django==6.0.6 对应 Py3.12，匹配。）
# -----------------------------------------------------------------------------
COPY requirements-server.txt /tmp/requirements-server.txt
RUN /opt/mambaforge/envs/ab17978/bin/pip install --upgrade pip \
 && /opt/mambaforge/envs/ab17978/bin/pip install -r /tmp/requirements-server.txt

# -----------------------------------------------------------------------------
# 4) mod_wsgi 4.9.4 编译进 Python 3.12 环境
#    - 4.9.0+ 才支持 Python 3.10+；4.9.4 稳定。
#    - 编译产物 mod_wsgi.so 装到 httpd 模块目录，并写 10-wsgi.conf 加载。
#    - LoadFile 指定 libpython3.12.so，否则 mod_wsgi 找不到 Python 运行时。
#    （用 ARG 固定版本，便于日后升级时只改一处。）
# -----------------------------------------------------------------------------
ARG MOD_WSGI_VERSION=4.9.4
RUN cd /tmp \
 && wget -q https://github.com/GrahamDumpleton/mod_wsgi/archive/refs/tags/${MOD_WSGI_VERSION}.tar.gz \
 && tar xf ${MOD_WSGI_VERSION}.tar.gz && cd mod_wsgi-${MOD_WSGI_VERSION} \
 && /opt/mambaforge/envs/ab17978/bin/python3.12 configure.py \
      --with-python=/opt/mambaforge/envs/ab17978/bin/python3.12 \
 && make -j"$(nproc)" && make install \
 && cd / && rm -rf /tmp/mod_wsgi-${MOD_WSGI_VERSION}* \
 && printf 'LoadModule wsgi_module /usr/lib64/httpd/modules/mod_wsgi.so\nLoadFile /opt/mambaforge/envs/ab17978/lib/libpython3.12.so.1.0\n' \
    > /etc/httpd/conf.modules.d/10-wsgi.conf

# -----------------------------------------------------------------------------
# 5) 固定生产 settings —— 容器内所有 manage.py / wsgi / loaddata 统一读它
#    （rjtian 负责在仓库放 myweb/settings_prod.py；若没放，构建这里会报错提示。）
# -----------------------------------------------------------------------------
ENV DJANGO_SETTINGS_MODULE=myweb.settings_prod

# -----------------------------------------------------------------------------
# 6) 容器内 Apache 站点配置（cluster 模式用：子路径 /ab17978）
#    standalone 模式不读它（waitress 直接服务），留着无害。
# -----------------------------------------------------------------------------
COPY ab17978.httpd.conf /etc/httpd/conf.d/ab17978.conf

# SQLite 业务表 schema（managed=False 的表靠它建；entrypoint 启动时幂等执行）
COPY sqlite_schema.sql /sqlite_schema.sql

# -----------------------------------------------------------------------------
# 7) 启动入口
# -----------------------------------------------------------------------------
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
