from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from web.views import AntimicrobialPeptideViewSet, PromoterViewSet, OperonViewSet, SrnaStructureViewSet, genome_tree, genome_tree_newick, genome_list, download_list, download_file, genes_data, genes_search, genes_context, genes_region, blast_run, gene_structure, srna_structure_image, gene_dna_sequence, primer_design

router = DefaultRouter()
router.register(r"antimicrobial-peptides", AntimicrobialPeptideViewSet)
router.register(r"promoters", PromoterViewSet)
router.register(r"operons", OperonViewSet)
router.register(r"srna-structures", SrnaStructureViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/genome/tree/", genome_tree, name="genome-tree"),
    path("api/genome/tree/newick/", genome_tree_newick, name="genome-tree-newick"),
    path("api/genome/list/", genome_list, name="genome-list"),
    path("api/download/list/", download_list, name="download-list"),
    path("api/download/file/", download_file, name="download-file"),
    path("api/genes/data/", genes_data, name="genes-data"),
    path("api/genes/search/", genes_search, name="genes-search"),
    path("api/genes/context/", genes_context, name="genes-context"),
    path("api/genes/region/", genes_region, name="genes-region"),
    path("api/blast/run/", blast_run, name="blast-run"),
    path("api/genes/structure/", gene_structure, name="gene-structure"),
    path("api/srna-structure-image/", srna_structure_image, name="srna-structure-image"),
    path("api/genes/dna-sequence/", gene_dna_sequence, name="gene-dna-sequence"),
    path("api/primers/design/", primer_design, name="primer-design"),
]

from django.urls import re_path
from django.views.generic import TemplateView

urlpatterns += [
    # 非 API / 非静态路径全部回退到前端 index.html（Vue history 模式）
    re_path(r"^(?!api/|admin/|static/).*$", TemplateView.as_view(template_name="index.html")),
]
