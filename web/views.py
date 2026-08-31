import os
import re
import tempfile
import subprocess
from django.conf import settings
from django.http import FileResponse, JsonResponse, HttpResponse
from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import SequenceData, PromoterData, OperonData, SrnaStructure
from .serializers import (
    AntimicrobialPeptideSerializer,
    PromoterSerializer,
    OperonSerializer,
    SrnaStructureSerializer,
)
from .pagination import CustomPageNumberPagination
from .genome_data import (
    get_tree_json, get_all_genome_stats, get_genes_data,
    search_genes, get_gene_context, get_region_features,
    TREE_FILE,
)

# ============================================================
#  基础路径配置 (推荐在 Django settings.py 中定义，此处设默认备选值)
# ============================================================
BASE_DATA_DIR = getattr(settings, 'BACTERIA_DATA_DIR', r"C:\Users\ymh\Desktop\bacteria")

GENOME_DB_PATH = getattr(settings, 'GENOME_DB_PATH', os.path.join(BASE_DATA_DIR, "GENOME_DB"))
BLAST_DIR = getattr(settings, 'BLAST_DIR', os.path.join(BASE_DATA_DIR, "BLAST_DB"))
BLAST_DB = getattr(settings, 'BLAST_DB', os.path.join(BLAST_DIR, "ab17978_db"))
BLAST_BIN = getattr(settings, 'BLAST_BIN', r"D:\NCBI-blast\blast-2.17.0+\bin\blastp.exe")

STRUCTURE_DIR = os.path.join(BASE_DATA_DIR, "extracted_cif_all")
GFF3_FILE = os.path.join(BASE_DATA_DIR, "final_merged_annotation.gff3")
GENOME_FNA = os.path.join(BASE_DATA_DIR, "Ab17978.fna")
SRNA_PNG_DIR = os.path.join(BASE_DATA_DIR, "rna_structure", "structure_png")


# ============================================================
#  模型视图集 (DRF ViewSets)
# ============================================================

class AntimicrobialPeptideViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ab17978 菌序列数据接口：支持筛选与统计
    """
    queryset = SequenceData.objects.all().order_by("seq_id")
    serializer_class = AntimicrobialPeptideSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["seq_id", "description", "sequence"]

    def get_queryset(self):
        """
        处理前端发来的筛选参数
        """
        queryset = super().get_queryset()
        params = self.request.query_params

        # Seq ID 精确搜索
        seq_id = params.get("seq_id")
        if seq_id:
            queryset = queryset.filter(seq_id__iexact=seq_id.strip())

        # Description 模糊搜索
        description = params.get("description")
        if description:
            queryset = queryset.filter(description__icontains=description.strip())

        # 序列模糊搜索
        sequence = params.get("sequence")
        if sequence:
            queryset = queryset.filter(sequence__icontains=sequence.strip())

        # 序列长度范围
        seq_length_min = params.get("seq_length_min")
        if seq_length_min and seq_length_min.isdigit():
            queryset = queryset.filter(seq_length__gte=int(seq_length_min))

        seq_length_max = params.get("seq_length_max")
        if seq_length_max and seq_length_max.isdigit():
            queryset = queryset.filter(seq_length__lte=int(seq_length_max))

        return queryset

    @action(detail=False, methods=["get"])
    def length_stats(self, request):
        """序列长度分布统计"""
        db_stats = (
            SequenceData.objects.values("seq_length")
            .annotate(count=Count("id"))
            .order_by("seq_length")
        )
        if not db_stats:
            return Response([])

        stats_dict = {
            item["seq_length"]: item["count"]
            for item in db_stats
            if item["seq_length"] is not None
        }
        
        if not stats_dict:
            return Response([])

        max_len = max(stats_dict.keys())
        continuous_stats = [
            {"length": l, "count": stats_dict.get(l, 0)}
            for l in range(1, max_len + 1)
        ]
        return Response(continuous_stats)


class PromoterViewSet(viewsets.ReadOnlyModelViewSet):
    """启动子活性数据接口"""
    queryset = PromoterData.objects.all().order_by("-mean_tpm_global")
    serializer_class = PromoterSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["gene_id"]


class OperonViewSet(viewsets.ReadOnlyModelViewSet):
    """操纵子分类数据接口"""
    queryset = OperonData.objects.all().order_by("id")
    serializer_class = OperonSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["classification", "rockhopper_range", "genes"]


class SrnaStructureViewSet(viewsets.ReadOnlyModelViewSet):
    """sRNA结构数据接口"""
    queryset = SrnaStructure.objects.all().order_by("name")
    serializer_class = SrnaStructureSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


# ============================================================
#  Genome API endpoints
# ============================================================

@api_view(["GET"])
def genome_tree(request):
    """Return the Newick tree parsed as ECharts-compatible JSON."""
    tree = get_tree_json()
    return Response(tree)


@api_view(["GET"])
def genome_tree_newick(request):
    """Return the raw Newick tree string (for Phylocanvas.gl)."""
    if not os.path.isfile(TREE_FILE):
        return JsonResponse({"error": "Tree file not found"}, status=404)
    with open(TREE_FILE, "r", encoding="utf-8") as f:
        newick = f.read().strip()
    return HttpResponse(newick, content_type="text/plain; charset=utf-8")


@api_view(["GET"])
def genome_list(request):
    """Return genome statistics for all .fna files."""
    stats = get_all_genome_stats()
    return Response(stats)


# ============================================================
#  Genes API endpoint
# ============================================================

@api_view(["GET"])
def genes_data(request):
    """Return Ab17978 genome annotation data for visualization."""
    data = get_genes_data()
    return Response(data)


@api_view(["GET"])
def genes_search(request):
    """Search genes by keyword (locus_tag, gene name, product)."""
    query = request.GET.get("q", "").strip()
    if not query:
        return Response([])
    results = search_genes(query)
    return Response(results)


@api_view(["GET"])
def genes_context(request):
    """Get genomic context around a specific gene."""
    locus_tag = request.GET.get("locus_tag", "").strip()
    replicon = request.GET.get("replicon", None)
    
    try:
        radius = int(request.GET.get("radius", 5000))
    except ValueError:
        radius = 5000

    if not locus_tag:
        return JsonResponse({"error": "Missing locus_tag parameter"}, status=400)
    
    data = get_gene_context(locus_tag, replicon, radius)
    return Response(data)


@api_view(["GET"])
def genes_region(request):
    """Query features in an arbitrary genomic region (for IGV dynamic loading)."""
    replicon = request.GET.get("replicon", "").strip()
    start = request.GET.get("start", "0").strip()
    end = request.GET.get("end", "0").strip()

    if not replicon or not start or not end:
        return JsonResponse({"error": "Missing replicon, start, or end parameter"}, status=400)

    try:
        start_int = int(start)
        end_int = int(end)
    except ValueError:
        return JsonResponse({"error": "Start and end must be integers"}, status=400)

    data = get_region_features(replicon, start_int, end_int)
    return Response(data)


# ============================================================
#  Structure & DNA Data Loaders
# ============================================================

_gene_coords = None
_genome_seqs = None


def _load_gff3():
    """Parse GFF3 and build locus_tag -> {seqid, start, end, strand} mapping."""
    global _gene_coords
    if _gene_coords is not None:
        return _gene_coords

    _gene_coords = {}
    if not os.path.isfile(GFF3_FILE):
        return _gene_coords

    with open(GFF3_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 9 or cols[2] != "CDS":
                continue

            seqid = cols[0]
            try:
                start = int(cols[3])
                end = int(cols[4])
            except ValueError:
                continue

            strand = cols[6]
            attrs = "\t".join(cols[8:])
            
            locus = ""
            for part in attrs.split(";"):
                if part.startswith("locus_tag="):
                    locus = part.split("=", 1)[1].strip()
                    break

            if locus:
                _gene_coords[locus] = {
                    "seqid": seqid,
                    "start": start,
                    "end": end,
                    "strand": strand,
                }
    return _gene_coords


def _load_genome():
    """Load genome FASTA into a dict keyed by seqid."""
    global _genome_seqs
    if _genome_seqs is not None:
        return _genome_seqs

    _genome_seqs = {}
    if not os.path.isfile(GENOME_FNA):
        return _genome_seqs

    current_id = None
    current_seq = []
    with open(GENOME_FNA, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_id:
                    _genome_seqs[current_id] = "".join(current_seq)
                current_id = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line.upper())

        if current_id:
            _genome_seqs[current_id] = "".join(current_seq)

    return _genome_seqs


@api_view(["GET"])
def gene_dna_sequence(request):
    """Return the DNA sequence for a given locus_tag."""
    locus_tag = request.GET.get("locus_tag", "").strip()
    if not locus_tag:
        return JsonResponse({"error": "Missing locus_tag"}, status=400)

    coords = _load_gff3()
    genome = _load_genome()

    if locus_tag not in coords:
        return JsonResponse({"error": f"Locus tag not found: {locus_tag}"}, status=404)

    coord = coords[locus_tag]
    seqid = coord["seqid"]

    if seqid not in genome:
        return JsonResponse({"error": f"Sequence not found for: {seqid}"}, status=404)

    seq = genome[seqid]
    start = coord["start"] - 1
    end = coord["end"]
    dna = seq[start:end]

    if coord["strand"] == "-":
        comp = str.maketrans("ATCGNRYKMSWBDHV", "TAGCNRYMKWSVHDB")
        dna = dna.translate(comp)[::-1]

    return JsonResponse({
        "locus_tag": locus_tag,
        "seqid": seqid,
        "start": coord["start"],
        "end": coord["end"],
        "strand": coord["strand"],
        "length": len(dna),
        "sequence": dna,
    })


@api_view(["POST"])
def primer_design(request):
    """Design PCR primers using Primer3."""
    import primer3

    sequence = (request.data.get("sequence", "") or "").strip()
    if not sequence or len(sequence) < 36:
        return JsonResponse({"error": "Sequence too short (min 36 bp required)"}, status=400)

    # 格式化并校验 DNA 序列
    seq = sequence.upper().replace("\n", "").replace(" ", "")
    if not re.match(r'^[ATCGNRYKMSWBDHV]+$', seq):
        return JsonResponse({"error": "Sequence contains invalid characters"}, status=400)

    try:
        p_min_size = int(request.data.get("primer_min_size", 18))
        p_max_size = int(request.data.get("primer_max_size", 25))
        p_opt_size = int(request.data.get("primer_opt_size", 20))
        prod_min = int(request.data.get("product_min", 80))
        prod_max = int(request.data.get("product_max", 1000))
    except ValueError:
        return JsonResponse({"error": "Invalid numerical parameters"}, status=400)

    params = {
        "PRIMER_NUM_RETURN": 10,
        "PRIMER_MIN_SIZE": p_min_size,
        "PRIMER_MAX_SIZE": p_max_size,
        "PRIMER_OPT_SIZE": p_opt_size,
        "PRIMER_MIN_TM": float(request.data.get("primer_min_tm", 55.0)),
        "PRIMER_MAX_TM": float(request.data.get("primer_max_tm", 65.0)),
        "PRIMER_OPT_TM": float(request.data.get("primer_opt_tm", 60.0)),
        "PRIMER_MIN_GC": float(request.data.get("primer_min_gc", 40.0)),
        "PRIMER_MAX_GC": float(request.data.get("primer_max_gc", 60.0)),
        "PRIMER_PRODUCT_SIZE_RANGE": [[prod_min, prod_max]],
        "PRIMER_MAX_POLY_X": 4,
        "PRIMER_GC_CLAMP": 1,
    }

    try:
        # 新版/旧版 Primer3 接口适配兼容
        design_func = getattr(primer3, 'design_primers', None) or getattr(primer3.bindings, 'design_primers', None)
        if not design_func:
            return JsonResponse({"error": "Primer3 bindings not found"}, status=500)

        result = design_func(
            {"SEQUENCE_ID": "template", "SEQUENCE_TEMPLATE": seq},
            params,
        )
    except Exception as e:
        return JsonResponse({"error": f"Primer3 calculation failed: {str(e)}"}, status=500)

    num_returned = result.get("PRIMER_PAIR_NUM_RETURNED", 0)
    pairs = []
    for i in range(num_returned):
        # 兼容 PRIMER_LEFT_i 是列表/元组 (start, length) 或者直接数值的情况
        left_info = result.get(f"PRIMER_LEFT_{i}")
        right_info = result.get(f"PRIMER_RIGHT_{i}")
        fwd_len = left_info[1] if isinstance(left_info, (list, tuple)) else left_info
        rev_len = right_info[1] if isinstance(right_info, (list, tuple)) else right_info

        pairs.append({
            "rank": i + 1,
            "fwd_seq": result.get(f"PRIMER_LEFT_{i}_SEQUENCE", ""),
            "fwd_len": fwd_len,
            "fwd_tm": round(result.get(f"PRIMER_LEFT_{i}_TM", 0), 1),
            "fwd_gc": round(result.get(f"PRIMER_LEFT_{i}_GC_PERCENT", 0), 1),
            "rev_seq": result.get(f"PRIMER_RIGHT_{i}_SEQUENCE", ""),
            "rev_len": rev_len,
            "rev_tm": round(result.get(f"PRIMER_RIGHT_{i}_TM", 0), 1),
            "rev_gc": round(result.get(f"PRIMER_RIGHT_{i}_GC_PERCENT", 0), 1),
            "product_size": result.get(f"PRIMER_PAIR_{i}_PRODUCT_SIZE", 0),
            "penalty": round(result.get(f"PRIMER_PAIR_{i}_PENALTY", 0), 2),
        })

    return JsonResponse({"pairs": pairs, "num_returned": num_returned})


@api_view(["GET"])
def gene_structure(request):
    """Check if a structure file exists for the given locus_tag, and return its content."""
    locus_tag = request.GET.get("locus_tag", "").strip()
    if not locus_tag:
        return JsonResponse({"error": "Missing locus_tag"}, status=400)

    # 过滤非标准字符，防止文件名注入
    safe_locus = re.sub(r'[^a-zA-Z0-9_\-]', '', locus_tag)

    if not os.path.isdir(STRUCTURE_DIR):
        return JsonResponse({"found": False, "reason": "Structure directory not found"})

    for fname in os.listdir(STRUCTURE_DIR):
        if fname.startswith(safe_locus + "_") and (fname.endswith(".cif") or fname.endswith(".pdb")):
            fpath = os.path.join(STRUCTURE_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                return JsonResponse({"found": False, "reason": f"Failed to read file: {str(e)}"})

            ext = os.path.splitext(fname)[1].lower()
            return JsonResponse({
                "found": True,
                "filename": fname,
                "format": ext.lstrip("."),
                "content": content,
            })

    return JsonResponse({"found": False, "reason": "No structure file"})


@api_view(["GET"])
def srna_structure_image(request):
    """Serve sRNA structure PNG image files."""
    name = request.GET.get("name", "").strip()
    stype = request.GET.get("type", "ss").strip()  # ss or dp
    
    if not name:
        return JsonResponse({"error": "Missing name"}, status=400)

    # 路径安全净化
    safe_name = os.path.basename(name)
    safe_stype = os.path.basename(stype)

    fname = f"{safe_name}_{safe_stype}.png"
    fpath = os.path.join(SRNA_PNG_DIR, fname)

    if not os.path.isfile(fpath):
        return JsonResponse({"error": "Image not found"}, status=404)

    return FileResponse(open(fpath, "rb"), content_type="image/png")


# ============================================================
#  BLAST API endpoint
# ============================================================

@api_view(["POST"])
def blast_run(request):
    """Run BLASTP against the Ab17978 sequence database."""
    sequence = request.data.get("sequence", "").strip()
    uploaded_file = request.FILES.get("file")

    query_fasta = ""
    if uploaded_file:
        try:
            query_fasta = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return JsonResponse({"error": f"无法读取上传文件: {str(e)}"}, status=400)
    elif sequence:
        if not sequence.startswith(">"):
            query_fasta = f">User_Query\n{sequence}"
        else:
            query_fasta = sequence
    else:
        return JsonResponse({"error": "请提供序列或上传FASTA文件"}, status=400)

    evalue = str(request.data.get("evalue", "10")).strip()
    matrix = str(request.data.get("matrix", "BLOSUM62")).strip()

    # 安全检查：限制矩阵只允许合法值，防止命令行参数注入
    allowed_matrices = ["BLOSUM45", "BLOSUM62", "BLOSUM80", "PAM30", "PAM70"]
    if matrix.upper() not in allowed_matrices:
        matrix = "BLOSUM62"

    if not os.path.isfile(BLAST_BIN):
        return JsonResponse({"error": "BLAST+ 未安装或可执行文件路径配置错误"}, status=500)
    if not os.path.isfile(BLAST_DB + ".pin") and not os.path.isfile(BLAST_DB + ".phr"):
        return JsonResponse({"error": "BLAST 数据库文件不存在"}, status=500)

    query_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False, encoding="utf-8"
        ) as f:
            f.write(query_fasta)
            query_path = f.name

        cmd = [
            BLAST_BIN,
            "-query", query_path,
            "-db", BLAST_DB,
            "-evalue", evalue,
            "-matrix", matrix,
            "-outfmt", "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qseq sseq",
            "-num_threads", "1",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            return JsonResponse({"error": result.stderr or "BLAST 运行失败"}, status=500)

        return JsonResponse({"result": result.stdout})

    except subprocess.TimeoutExpired:
        return JsonResponse({"error": "BLAST 比对超时（超过 120 秒）"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        if query_path and os.path.exists(query_path):
            os.unlink(query_path)