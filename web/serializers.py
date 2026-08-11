from rest_framework import serializers
from .models import SequenceData, PromoterData, OperonData, SrnaStructure


class AntimicrobialPeptideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceData
        fields = "__all__"


class PromoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoterData
        fields = "__all__"


class OperonSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperonData
        fields = "__all__"


class SrnaStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SrnaStructure
        fields = "__all__"
