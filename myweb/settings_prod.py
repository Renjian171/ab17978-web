"""
Ab17978 生产配置（容器内用）。
继承 settings.py 全部默认值，仅覆盖生产所需项。
"""
from .settings import *  # noqa
import os

# 数据库：SQLite（容器内本地文件）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/home/rjtian/ab17978-data/db.sqlite3",
    }
}

# 基因组 / BLAST 数据目录（容器内绝对路径，宿主同路径挂载）
BACTERIA_DATA_DIR = r"/home/rjtian/bacteria"
BLAST_BIN = r"/opt/mambaforge/envs/ab17978/bin/blastp"

# 前端构建产物
WHITENOISE_ROOT = r"/home/rjtian/dist"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
TEMPLATES[0]["DIRS"] = [
    os.path.join(BASE_DIR, "templates"),
    r"/home/rjtian/dist",
]

# whitenoise 中间件插到 SecurityMiddleware 之后
_mw = list(MIDDLEWARE)
if "whitenoise.middleware.WhiteNoiseMiddleware" not in _mw:
    try:
        i = _mw.index("django.middleware.security.SecurityMiddleware")
        _mw.insert(i + 1, "whitenoise.middleware.WhiteNoiseMiddleware")
    except ValueError:
        _mw.insert(0, "whitenoise.middleware.WhiteNoiseMiddleware")
MIDDLEWARE = _mw

# 安全 / 生产开关
DEBUG = False
ALLOWED_HOSTS = ["cbi.gxu.edu.cn", "localhost", "127.0.0.1", "172.21.66.13"]
# 子路径 /ab17978 由 mod_wsgi 的 WSGIScriptAlias 自动处理，不设 FORCE_SCRIPT_NAME
