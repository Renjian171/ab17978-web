# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AmpData(models.Model):
    amp_id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=255, blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    family = models.CharField(max_length=255, blank=True, null=True)
    gene = models.CharField(max_length=255, blank=True, null=True)
    activity = models.TextField(blank=True, null=True)
    sequence = models.TextField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    hydrophobicity = models.FloatField(blank=True, null=True)
    boman_index = models.FloatField(blank=True, null=True)
    formula = models.CharField(max_length=255, blank=True, null=True)
    half_life = models.CharField(max_length=255, blank=True, null=True)
    mass = models.FloatField(blank=True, null=True)
    pi = models.FloatField(blank=True, null=True)
    structure = models.CharField(max_length=255, blank=True, null=True)
    structure_description = models.TextField(blank=True, null=True)
    smiles_string = models.TextField(blank=True, null=True)
    n_terminal_mod = models.CharField(max_length=255, blank=True, null=True)
    c_terminal_mod = models.CharField(max_length=255, blank=True, null=True)
    other_modifications = models.TextField(blank=True, null=True)
    linear_cyclic_branched = models.CharField(max_length=100, blank=True, null=True)
    stereochemistry = models.CharField(max_length=100, blank=True, null=True)
    swissprot_id = models.CharField(max_length=100, blank=True, null=True)
    pdb_id = models.CharField(max_length=100, blank=True, null=True)
    activity_against_target = models.TextField(blank=True, null=True)
    cytotoxicity = models.TextField(blank=True, null=True)
    target_objects = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    reference = models.TextField(blank=True, null=True)
    pubmed_id = models.BigIntegerField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'amp_data'
