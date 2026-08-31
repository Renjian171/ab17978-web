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
from django.views.decorators.http import require_http_methods

# 发布台账：每发布一个文件，在此登记一条。
# 文件名必须与宿主机 /home/download/ab17978/ 内的文件完全一致（含大小写）。
# 台账与目录必须同步：目录里有而台账没有 = 用户看不到；台账有而目录没有 = 302 后 404。
# 命名规范：仅 [A-Za-z0-9._-]，无空格；更新版本用新文件名（如 _v2），旧版本台账与目录同步移除。
DOWNLOAD_MANIFEST = {
    'A_baumannii_17978.zip': {
        "size": '40.4M',
        "date": "2026-08-31",
        "desc": 'A. baumannii 17978',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_19606.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii 19606',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_6080.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii 6080',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_AB-18_FGL.zip': {
        "size": '1.3M',
        "date": "2026-08-31",
        "desc": 'A. baumannii AB-18_FGL',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_AB-38_FGL.zip': {
        "size": '1.3M',
        "date": "2026-08-31",
        "desc": 'A. baumannii AB-38_FGL',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_AB30.zip': {
        "size": '1.3M',
        "date": "2026-08-31",
        "desc": 'A. baumannii AB30',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_AC1633.zip': {
        "size": '1.3M',
        "date": "2026-08-31",
        "desc": 'A. baumannii AC1633',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_AF-401.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii AF-401',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_AR_0101.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii AR_0101',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_BAL114.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii BAL114',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_DETAB-E51.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii DETAB-E51',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_MRSN_58.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii MRSN 58',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_MRSN15313.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii MRSN15313',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_UC23022.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii UC23022',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_VB82.zip': {
        "size": '1.3M',
        "date": "2026-08-31",
        "desc": 'A. baumannii VB82',
        "genus": 'Acinetobacter',
    },
    'A_baumannii_XH1056.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. baumannii XH1056',
        "genus": 'Acinetobacter',
    },
    'A_bouvetii_JCM18991.zip': {
        "size": '1.0M',
        "date": "2026-08-31",
        "desc": 'A. bouvetii JCM18991',
        "genus": 'Acinetobacter',
    },
    'A_chenhuanii_XH1741.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. chenhuanii XH1741',
        "genus": 'Acinetobacter',
    },
    'A_corruptisaponis_KCTC_92772.zip': {
        "size": '1.2M',
        "date": "2026-08-31",
        "desc": 'A. corruptisaponis KCTC 92772',
        "genus": 'Acinetobacter',
    },
    'A_lanii_185.zip': {
        "size": '1.0M',
        "date": "2026-08-31",
        "desc": 'A. lanii 185',
        "genus": 'Acinetobacter',
    },
    'A_larvae_BRTC-1.zip': {
        "size": '1.1M',
        "date": "2026-08-31",
        "desc": 'A. larvae BRTC-1',
        "genus": 'Acinetobacter',
    },
    'A_lwoffii_DSM2403.zip': {
        "size": '1.0M',
        "date": "2026-08-31",
        "desc": 'A. lwoffii DSM2403',
        "genus": 'Acinetobacter',
    },
    'A_tibetensis_Y-23.zip': {
        "size": '1.0M',
        "date": "2026-08-31",
        "desc": 'A. tibetensis Y-23',
        "genus": 'Acinetobacter',
    },
    'P_entomophila_L48.zip': {
        "size": '1.7M',
        "date": "2026-08-31",
        "desc": 'P. entomophila L48',
        "genus": 'Pseudomonas',
    },
    'P_monsensis_PGSB_8459.zip': {
        "size": '1.9M',
        "date": "2026-08-31",
        "desc": 'P. monsensis PGSB 8459',
        "genus": 'Pseudomonas',
    },
    'P_protegens_CHA0.zip': {
        "size": '2.0M',
        "date": "2026-08-31",
        "desc": 'P. protegens CHA0',
        "genus": 'Pseudomonas',
    },
    'P_putida_NBRC_14164.zip': {
        "size": '1.8M',
        "date": "2026-08-31",
        "desc": 'P. putida NBRC 14164',
        "genus": 'Pseudomonas',
    },
    'P_synxantha_NCTC10696.zip': {
        "size": '2.0M',
        "date": "2026-08-31",
        "desc": 'P. synxantha NCTC10696',
        "genus": 'Pseudomonas',
    },
    'GTDB-Tk_Phylogenetic_Tree.zip': {
        "size": '0.7K',
        "date": "2026-08-31",
        "desc": 'GTDB-Tk Phylogenetic Tree (Newick)',
        "genus": 'Other',
    },
}

# 与 download_links 的 FilesMatch 清单保持同步（管理员维护，勿自行扩大）
ALLOWED_EXT = {".zip"}


@require_http_methods(["GET", "HEAD"])
def download_list(request):
    """① 列表 API：返回 JSON，前端据此渲染下载按钮"""
    files = [{"name": name, **meta} for name, meta in DOWNLOAD_MANIFEST.items()]
    return JsonResponse({"files": files})


@require_http_methods(["GET", "HEAD"])
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
