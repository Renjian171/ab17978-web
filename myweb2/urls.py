"""
URL configuration for myweb2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 1. 这里修改：把 run_blast 一并导入进来
from web.views import AntimicrobialPeptideViewSet, run_blast

# 注册视图集路由
router = DefaultRouter()
router.register(
    r"antimicrobial-peptides", AntimicrobialPeptideViewSet
)  # 接口路径：/antimicrobial-peptides/

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),  # API接口根路径：/api/
    # 2. 这里修改：新增 BLAST 的 API 路由
    path("api/blast/run/", run_blast, name="run-blast"),
]
