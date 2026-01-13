from django.db import models


class AntimicrobialPeptide(models.Model):
    """抗菌肽数据表模型（与MySQL的antimicrobial_peptides表映射）"""

    # 主键字段（对应MySQL的apd_id，设为主键）
    apd_id = models.CharField(
        max_length=20, primary_key=True, verbose_name="抗菌肽唯一ID"
    )
    # 基本信息字段（对应MySQL的text/varchar字段）
    name_class = models.TextField(null=True, blank=True, verbose_name="名称/分类")
    source = models.TextField(null=True, blank=True, verbose_name="来源生物/组织")
    sequence = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="氨基酸序列"
    )
    # 数值型字段（对应MySQL的int/decimal字段）
    length = models.IntegerField(null=True, blank=True, verbose_name="序列长度")
    net_charge = models.IntegerField(null=True, blank=True, verbose_name="净电荷")
    hydrophobic_residue_pct = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="疏水残基百分比"
    )
    boman_index = models.DecimalField(
        max_digits=5,  # 总位数（如14.92是4位，预留1位冗余）
        decimal_places=2,  # 小数位数（与MySQL一致）
        null=True,
        blank=True,
        verbose_name="博曼指数",
    )
    # 其他字段（按MySQL表结构依次映射）
    three_d_structure = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="3D结构类型"
    )
    method = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="测定方法"
    )
    swiss_prot_id = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="SwissProt ID"
    )
    activity = models.TextField(null=True, blank=True, verbose_name="抗菌活性描述")
    crucial_residues = models.TextField(
        null=True, blank=True, verbose_name="关键残基信息"
    )
    additional_info = models.TextField(  # Django无LONGTEXT，用TextField足够（支持4GB）
        null=True, blank=True, verbose_name="附加信息"
    )
    title = models.TextField(null=True, blank=True, verbose_name="文献标题")
    author = models.TextField(null=True, blank=True, verbose_name="文献作者")
    reference = models.TextField(null=True, blank=True, verbose_name="文献引用")

    class Meta:
        # 关键：指定映射的MySQL表名（必须与实际表名一致）
        db_table = "antimicrobial_peptides"
        verbose_name = "抗菌肽数据"
        verbose_name_plural = "抗菌肽数据表"  # 复数形式（避免Django自动加s）

    def __str__(self):
        # 后台管理显示时，用“ID+名称”标识每条数据
        return f"{self.apd_id} - {self.name_class[:20]}"  # 截取前20字符避免过长
