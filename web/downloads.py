"""
发布台账 + 下载 API（方案 C：校验后 302 到节点统一静态出口）。

与管理员文档《DEPLOY_ab17978_download.md》对应：
  - 文件实体在宿主机 /home/download/ab17978/，由 docker_download_links 静态发出
    （自动 attachment 头、断点续传、-Indexes 保护）
  - 本容器只维护"发布台账"（文件名 → 元数据），不做文件流回传
    （规范 2：站点内禁止裸下载直链，HTML/JS 源码中不出现 *.zip 直链）
"""
import os
import urllib.parse

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

# 发布台账：每发布一个文件，在此登记一条。
# 文件名必须与宿主机 /home/download/ab17978/ 内的文件完全一致（含大小写）。
# 台账与目录必须同步：目录里有而台账没有 = 用户看不到；台账有而目录没有 = 302 后 404。
DOWNLOAD_MANIFEST = {
    "A_baumannii_17978.zip": {
        "size": "41M",            # 展示用
        "date": "2026-08-31",     # 发布日期
        "desc": "A. baumannii 17978 基因组与注释数据集",
    },
}

# 与 download_links 的 FilesMatch 清单保持同步（管理员维护，勿自行扩大）
ALLOWED_EXT = {".zip"}


@require_GET
def download_list(request):
    """① 列表 API：返回 JSON，前端据此渲染下载按钮"""
    files = [{"name": name, **meta} for name, meta in DOWNLOAD_MANIFEST.items()]
    return JsonResponse({"files": files})


@require_GET
def download_file(request):
    """② 下载 API：三层校验后 302 到统一静态出口"""
    name = request.GET.get("file", "")

    # 校验 1：防路径穿越——basename 必须原样相等（挡 ../、子目录、反斜杠）
    if name != os.path.basename(name) or ".." in name:
        return JsonResponse({"error": "invalid file name"}, status=400)

    # 校验 2：后缀白名单
    if os.path.splitext(name)[1].lower() not in ALLOWED_EXT:
        return JsonResponse({"error": "file type not allowed"}, status=400)

    # 校验 3：台账精确匹配（防枚举、防 404 探测）
    if name not in DOWNLOAD_MANIFEST:
        return JsonResponse({"error": "file not found"}, status=404)

    # 302 到静态出口。Location 必须是域名根的绝对路径（/downloadFiles 不在 /ab17978 下）
    return HttpResponse(
        status=302,
        headers={"Location": f"/downloadFiles/ab17978/{urllib.parse.quote(name)}"},
    )
