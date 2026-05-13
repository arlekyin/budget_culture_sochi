from rest_framework import serializers
from .models import FactPayment, Reservation


class FactPaymentSerializer(serializers.ModelSerializer):
    institution_name = serializers.StringRelatedField(source='institution')
    kosgu_display = serializers.StringRelatedField(source='kosgu')
    added_by_name = serializers.SerializerMethodField()

    class Meta:
        model = FactPayment
        fields = (
            'id', 'institution', 'institution_name', 'kosgu', 'kosgu_display',
            'year', 'amount', 'payment_date', 'description',
            'document_number', 'added_by', 'added_by_name', 'added_at',
        )
        read_only_fields = ('added_by', 'added_at')

    def get_added_by_name(self, obj) -> str:
        if obj.added_by:
            return obj.added_by.get_full_name() or obj.added_by.username
        return ''

    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)


class ReservationSerializer(serializers.ModelSerializer):
    institution_name = serializers.StringRelatedField(source='institution')
    kosgu_display = serializers.StringRelatedField(source='kosgu')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = (
            'id', 'institution', 'institution_name', 'kosgu', 'kosgu_display',
            'year', 'contract_number', 'contractor', 'amount', 'contract_date',
            'status', 'status_display', 'created_by', 'created_by_name',
            'created_at', 'note',
        )
        read_only_fields = ('created_by', 'created_at')

    def get_created_by_name(self, obj) -> str:
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return ''

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
