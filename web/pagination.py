# web/pagination.py
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    # 前端传递“每页条数”的参数名（必须与前端一致）
    page_size_query_param = "page_size"
    # 每页最大条数（覆盖settings.py的MAX_PAGE_SIZE）
    max_page_size = 100
