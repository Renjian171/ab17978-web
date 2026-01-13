# web/serializers.py
from rest_framework import serializers
from .models import AntimicrobialPeptide


class AntimicrobialPeptideSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntimicrobialPeptide
        fields = (
            "__all__"  # 序列化所有字段（也可指定具体字段，如['apd_id', 'sequence']）
        )
