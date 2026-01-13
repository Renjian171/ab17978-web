from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action  # 新增：导入 action 装饰器
from rest_framework.response import Response  # 新增：导入 Response
from django.db.models import Count  # 新增：导入聚合函数
from .models import AntimicrobialPeptide
from .serializers import AntimicrobialPeptideSerializer
from .pagination import CustomPageNumberPagination


class AntimicrobialPeptideViewSet(viewsets.ReadOnlyModelViewSet):
    """
    抗菌肽数据接口：支持分类搜索、范围搜索及高级组合搜索，以及数据统计
    """

    # 基础查询集
    queryset = AntimicrobialPeptide.objects.all()
    serializer_class = AntimicrobialPeptideSerializer
    pagination_class = CustomPageNumberPagination

    # 启用 DRF 搜索过滤后端
    filter_backends = [filters.SearchFilter]
    search_fields = ["apd_id", "name_class", "sequence", "activity", "source"]

    # --- 新增：统计图接口 ---
    @action(detail=False, methods=["get"])
    def length_stats(self, request):
        """
        获取连续长度分布数据：补全数量为 0 的长度区间
        """
        # 1. 获取数据库中存在的统计数据
        db_stats = (
            AntimicrobialPeptide.objects.values("length")
            .annotate(count=Count("apd_id"))
            .order_by("length")
        )

        if not db_stats:
            return Response([])

        # 2. 将数据库结果转换为字典，方便查询 {length: count}
        stats_dict = {item["length"]: item["count"] for item in db_stats}

        # 3. 获取长度的最大值和最小值
        min_len = db_stats[0]["length"]
        max_len = db_stats[len(db_stats) - 1]["length"]

        # 4. 补全中间缺失的长度，数量设为 0
        continuous_stats = []
        for l in range(1, max_len + 1):
            continuous_stats.append(
                {
                    "length": l,
                    "count": stats_dict.get(
                        l, 0
                    ),  # 如果字典里没有这个长度，说明数量为 0
                }
            )

        return Response(continuous_stats)

    # --- 新增：疏水性分布统计 ---
    @action(detail=False, methods=["get"])
    def hydro_stats(self, request):
        from django.db.models.functions import Cast
        from django.db.models import IntegerField, FloatField

        # 按照 10% 的间隔进行分组统计
        stats = []
        for i in range(0, 100, 10):
            count = AntimicrobialPeptide.objects.filter(
                hydrophobic_residue_pct__gte=i, hydrophobic_residue_pct__lt=i + 10
            ).count()
            stats.append({"range": f"{i}-{i+10}%", "count": count})
        return Response(stats)

    # --- 新增：物种来源 Top 10 ---
    @action(detail=False, methods=["get"])
    def source_stats(self, request):
        db_stats = (
            AntimicrobialPeptide.objects.values("source")
            .annotate(count=Count("apd_id"))
            .order_by("-count")[:10]  # 只取前 10 名
        )
        return Response(db_stats)

    def get_queryset(self):
        """
        核心逻辑：处理高级搜索和简单搜索
        """
        queryset = AntimicrobialPeptide.objects.all().order_by("apd_id")
        params = self.request.query_params

        # --- 高级搜索逻辑：精确/模糊匹配 ---
        if params.get("apd_id"):
            queryset = queryset.filter(apd_id__iexact=params.get("apd_id"))
        if params.get("name_class"):
            queryset = queryset.filter(name_class__icontains=params.get("name_class"))
        if params.get("source"):
            queryset = queryset.filter(source__icontains=params.get("source"))
        if params.get("sequence"):
            queryset = queryset.filter(sequence__icontains=params.get("sequence"))

        # --- 高级搜索逻辑：数值范围查询 ---
        if params.get("length_min"):
            queryset = queryset.filter(length__gte=params.get("length_min"))
        if params.get("length_max"):
            queryset = queryset.filter(length__lte=params.get("length_max"))

        if params.get("net_charge_min"):
            queryset = queryset.filter(net_charge__gte=params.get("net_charge_min"))
        if params.get("net_charge_max"):
            queryset = queryset.filter(net_charge__lte=params.get("net_charge_max"))

        if params.get("hydro_min"):
            queryset = queryset.filter(
                hydrophobic_residue_pct__gte=params.get("hydro_min")
            )
        if params.get("hydro_max"):
            queryset = queryset.filter(
                hydrophobic_residue_pct__lte=params.get("hydro_max")
            )

        # --- 兼容首页/列表页普通搜索逻辑 ---
        search_query = params.get("search")
        search_field = params.get("search_field", "all")

        if search_query:
            if search_field == "name":
                queryset = queryset.filter(name_class__icontains=search_query)
            elif search_field == "apd_id":
                queryset = queryset.filter(apd_id__iexact=search_query)
            elif search_field == "sequence":
                queryset = queryset.filter(sequence__icontains=search_query)

        return queryset
