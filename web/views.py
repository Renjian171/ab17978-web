from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q  # 必须导入 Q 对象用于组合查询
import math

from .models import AmpData
from .serializers import AntimicrobialPeptideSerializer
from .pagination import CustomPageNumberPagination
import os
import subprocess
from django.conf import settings
from rest_framework.decorators import api_view


class AntimicrobialPeptideViewSet(viewsets.ReadOnlyModelViewSet):
    """
    抗菌肽数据接口：支持多维度筛选与统计
    """

    queryset = AmpData.objects.all().order_by("amp_id")
    serializer_class = AntimicrobialPeptideSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [filters.SearchFilter]
    search_fields = ["amp_id", "name", "sequence", "activity", "source"]

    # ============================================================
    #  核心筛选逻辑 (修改重点)
    # ============================================================
    def get_queryset(self):
        """
        处理前端 AdvancedSearch.vue 发来的所有筛选参数
        """
        queryset = AmpData.objects.all().order_by("amp_id")
        params = self.request.query_params

        # --- 1. 文本模糊搜索 ---

        # ID 精确搜索
        if params.get("apd_id"):
            queryset = queryset.filter(amp_id__iexact=params.get("apd_id"))

        # 名称/分类 (混合搜索 Name, Family, Gene)
        if params.get("name_class"):
            v = params.get("name_class")
            queryset = queryset.filter(
                Q(name__icontains=v) | Q(family__icontains=v) | Q(gene__icontains=v)
            )

        # 来源
        if params.get("source"):
            queryset = queryset.filter(source__icontains=params.get("source"))

        # 活性 (新增)
        if params.get("activity"):
            queryset = queryset.filter(activity__icontains=params.get("activity"))

        # 靶标对象 (新增)
        if params.get("target_objects"):
            queryset = queryset.filter(
                target_objects__icontains=params.get("target_objects")
            )

        # 序列
        if params.get("sequence"):
            queryset = queryset.filter(sequence__icontains=params.get("sequence"))

        # --- 2. 数值范围搜索 ---

        # 长度 (Length)
        if params.get("length_min"):
            queryset = queryset.filter(length__gte=params.get("length_min"))
        if params.get("length_max"):
            queryset = queryset.filter(length__lte=params.get("length_max"))

        # 分子量 (Mass) - 新增
        if params.get("mass_min"):
            queryset = queryset.filter(mass__gte=params.get("mass_min"))
        if params.get("mass_max"):
            queryset = queryset.filter(mass__lte=params.get("mass_max"))

        # 等电点 (pI) - 新增
        if params.get("pi_min"):
            queryset = queryset.filter(pi__gte=params.get("pi_min"))
        if params.get("pi_max"):
            queryset = queryset.filter(pi__lte=params.get("pi_max"))

        # 疏水性 (Hydrophobicity)
        if params.get("hydro_min"):
            queryset = queryset.filter(hydrophobicity__gte=params.get("hydro_min"))
        if params.get("hydro_max"):
            queryset = queryset.filter(hydrophobicity__lte=params.get("hydro_max"))

        # 博曼指数 (Boman Index) - 新增
        if params.get("boman_min"):
            queryset = queryset.filter(boman_index__gte=params.get("boman_min"))
        if params.get("boman_max"):
            queryset = queryset.filter(boman_index__lte=params.get("boman_max"))

        return queryset

    # ============================================================
    #  统计接口 (保持原有逻辑，整理缩进)
    # ============================================================

    # --- 1. 长度分布 ---
    @action(detail=False, methods=["get"])
    def length_stats(self, request):
        db_stats = (
            AmpData.objects.values("length")
            .annotate(count=Count("amp_id"))
            .order_by("length")
        )
        if not db_stats:
            return Response([])

        stats_dict = {
            item["length"]: item["count"] for item in db_stats if item["length"]
        }
        lengths = [k for k in stats_dict.keys()]
        if not lengths:
            return Response([])

        max_len = max(lengths)
        continuous_stats = []
        for l in range(1, max_len + 1):
            continuous_stats.append({"length": l, "count": stats_dict.get(l, 0)})
        return Response(continuous_stats)

    # --- 2. 疏水性分布 ---
    @action(detail=False, methods=["get"])
    def hydro_stats(self, request):
        values = AmpData.objects.exclude(hydrophobicity__isnull=True).values_list(
            "hydrophobicity", flat=True
        )
        raw_bins = {}
        min_val, max_val = 0.0, 0.0
        has_data = False

        for val in values:
            try:
                v = float(val)
                has_data = True
                floor_val = math.floor(v * 10) / 10.0
                key = f"{floor_val:.1f}"
                raw_bins[key] = raw_bins.get(key, 0) + 1
                if v < min_val:
                    min_val = v
                if v > max_val:
                    max_val = v
            except:
                continue

        if not has_data:
            return Response([])

        start = math.floor(min_val * 10)
        end = math.ceil(max_val * 10)
        result = []
        for i in range(start, end + 1):
            current_val = i / 10.0
            key_str = f"{current_val:.1f}"
            next_val = (i + 1) / 10.0
            result.append(
                {
                    "range": f"{current_val:.1f} ~ {next_val:.1f}",
                    "count": raw_bins.get(key_str, 0),
                }
            )
        return Response(result)

    # --- 3. 来源分布 ---
    @action(detail=False, methods=["get"])
    def source_stats(self, request):
        db_stats = (
            AmpData.objects.values("source")
            .annotate(count=Count("amp_id"))
            .order_by("-count")[:10]
        )
        return Response(db_stats)

    # --- 4. 分子量分布 (Mass) ---
    @action(detail=False, methods=["get"])
    def mass_stats(self, request):
        values = AmpData.objects.exclude(mass__isnull=True).values_list(
            "mass", flat=True
        )
        bins = {}
        for val in values:
            try:
                v = float(val)
                bin_start = int(v // 500) * 500
                bins[bin_start] = bins.get(bin_start, 0) + 1
            except:
                continue
        sorted_keys = sorted(bins.keys())
        result = [{"range": f"{k}-{k+500}", "count": bins[k]} for k in sorted_keys]
        return Response(result)

    # --- 5. 等电点分布 (pI) ---
    @action(detail=False, methods=["get"])
    def pi_stats(self, request):
        values = AmpData.objects.exclude(pi__isnull=True).values_list("pi", flat=True)
        bins = {}
        for val in values:
            try:
                v = float(val)
                bin_start = int(v)
                bins[bin_start] = bins.get(bin_start, 0) + 1
            except:
                continue
        sorted_keys = sorted(bins.keys())
        result = [{"range": f"{k}-{k+1}", "count": bins[k]} for k in sorted_keys]
        return Response(result)

    # --- 6. 活性分布 (Activity) ---
    @action(detail=False, methods=["get"])
    def activity_stats(self, request):
        all_activities = AmpData.objects.exclude(activity__isnull=True).values_list(
            "activity", flat=True
        )
        activity_counts = {}
        for act_str in all_activities:
            if not act_str:
                continue
            parts = [x.strip() for x in act_str.replace(";", ",").split(",")]
            for p in parts:
                if p:
                    p = p.capitalize()
                    activity_counts[p] = activity_counts.get(p, 0) + 1
        sorted_acts = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
        result = [{"name": k, "value": v} for k, v in sorted_acts]
        return Response(result)


@api_view(["POST"])
def run_blast(request):
    """
    接收前端参数，运行本地 BLAST 引擎并返回结果
    """
    # 1. 接收前端传来的参数
    program = request.data.get("program", "blastp")
    database = request.data.get("database", "all")
    evalue = request.data.get("evalue", "0.05")
    matrix = request.data.get("matrix", "BLOSUM62")

    sequence_text = request.data.get("sequence", "")
    uploaded_file = request.FILES.get("file", None)

    # 2. 定义临时文件存放路径 (为了安全和整洁，放在项目根目录的 data 文件夹下)
    # 请确保你的 Django 项目根目录下有一个名为 'data' 的文件夹！
    temp_dir = os.path.join(settings.BASE_DIR, "data")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    temp_query_path = os.path.join(temp_dir, "temp_query.fasta")

    try:
        # 3. 处理输入数据，将其保存为临时 FASTA 文件
        if uploaded_file:
            with open(temp_query_path, "wb+") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        elif sequence_text:
            with open(temp_query_path, "w", encoding="utf-8") as f:
                # 检查用户输入是否包含 '>' (FASTA 头)，如果没有则自动补齐
                if not sequence_text.strip().startswith(">"):
                    f.write(">User_Query\n")
                f.write(sequence_text)
        else:
            return Response(
                {"error": "未提供序列文本或文件 (No sequence or file provided)."},
                status=400,
            )

        # 在 run_blast 函数中找到这里并替换

        # 4. 指定本地 BLAST 数据库路径
        db_path = os.path.join(temp_dir, "amp_db")

        # 获取 blastp.exe 的绝对路径 (请确保这里的路径是你电脑上的真实路径)
        blast_bin_dir = r"D:\NCBI-blast\blast-2.17.0+\bin"
        exe_name = f"{program}.exe" if os.name == "nt" else program
        exe_path = os.path.join(blast_bin_dir, exe_name)

        # 5. 构造命令行指令
        # 核心改动：增加 -outfmt 6 并指定具体需要的列
        # qseqid: 查询序列ID
        # sseqid: 目标序列ID (数据库里的AMP_ID)
        # pident: 相似度百分比 (Identity)
        # length: 匹配长度
        # mismatch: 错配数
        # gapopen: gap数
        # qstart, qend: query起始和结束位置
        # sstart, send: subject起始和结束位置
        # evalue: E值
        # bitscore: 得分
        cmd = [
            exe_path,
            "-query",
            temp_query_path,
            "-db",
            db_path,
            "-evalue",
            str(evalue),
            "-matrix",
            matrix,
            "-outfmt",
            "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq",
        ]

        # 6. 执行命令并捕获输出结果
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            return Response(
                {
                    "error": "BLAST 执行失败 (Execution failed).",
                    "details": result.stderr,
                },
                status=500,
            )

        # 7. 此时的 result.stdout 是一个由 Tab (\t) 分隔的文本字符串
        blast_output = result.stdout
        return Response({"result": blast_output})

    except Exception as e:
        return Response(
            {"error": "服务器内部错误 (Internal Server Error)", "details": str(e)},
            status=500,
        )

    finally:
        # 8. 无论成功失败，都清理掉刚才生成的临时输入文件
        if os.path.exists(temp_query_path):
            os.remove(temp_query_path)
