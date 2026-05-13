from rest_framework import serializers
from .models import Institution, BudgetLimit


class BudgetLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetLimit
        fields = ('id', 'year', 'total_limit', 'note', 'set_at')


class InstitutionSerializer(serializers.ModelSerializer):
    institution_type_display = serializers.CharField(
        source='get_institution_type_display', read_only=True
    )
    limits = BudgetLimitSerializer(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'short_name', 'institution_type',
            'institution_type_display', 'inn', 'address',
            'head_name', 'is_active', 'created_at', 'limits',
        )


class InstitutionListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор для списка учреждений."""

    institution_type_display = serializers.CharField(
        source='get_institution_type_display', read_only=True
    )

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'short_name', 'institution_type',
            'institution_type_display', 'address', 'head_name', 'is_active',
        )
