from django.db import models


class SequenceData(models.Model):
    id = models.AutoField(primary_key=True)
    seq_id = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    seq_length = models.IntegerField(blank=True, null=True)
    sequence = models.TextField(blank=True, null=True)
    molecular_weight = models.FloatField(blank=True, null=True)
    theoretical_pi = models.FloatField(blank=True, null=True)
    instability_index = models.FloatField(blank=True, null=True)
    aliphatic_index = models.FloatField(blank=True, null=True)
    gravy = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sequences'


class PromoterData(models.Model):
    id = models.AutoField(primary_key=True)
    gene_id = models.CharField(max_length=50)
    length = models.IntegerField(blank=True, null=True)
    mean_tpm_global = models.FloatField(blank=True, null=True)
    mean_tpm_lck = models.FloatField(blank=True, null=True)
    mean_tpm_sck = models.FloatField(blank=True, null=True)
    lck1 = models.FloatField(blank=True, null=True)
    lck2 = models.FloatField(blank=True, null=True)
    lck3 = models.FloatField(blank=True, null=True)
    sck1 = models.FloatField(blank=True, null=True)
    sck2 = models.FloatField(blank=True, null=True)
    sck3 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'promoters'


class OperonData(models.Model):
    id = models.AutoField(primary_key=True)
    rockhopper_range = models.CharField(max_length=50, blank=True, null=True)
    strand = models.CharField(max_length=5, blank=True, null=True)
    classification = models.CharField(max_length=30, blank=True, null=True)
    operon_mapper_id = models.CharField(max_length=20, blank=True, null=True)
    operon_mapper_range = models.CharField(max_length=50, blank=True, null=True)
    genes = models.TextField(blank=True, null=True)
    matched_id = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'operons'


class SrnaStructure(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    sequence = models.TextField(blank=True, null=True)
    seq_length = models.IntegerField(blank=True, null=True)
    mfe_structure = models.TextField(blank=True, null=True)
    mfe_energy = models.CharField(max_length=20, blank=True, null=True)
    diversity = models.CharField(max_length=20, blank=True, null=True)
    centroid_structure = models.TextField(blank=True, null=True)
    centroid_energy = models.CharField(max_length=20, blank=True, null=True)
    mec_structure = models.TextField(blank=True, null=True)
    mec_energy = models.CharField(max_length=20, blank=True, null=True)
    frequency = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'srna_structures'
