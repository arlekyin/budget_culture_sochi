from rest_framework import serializers
from .models import BudgetRequest, RequestLine, RequestLineLog, RequestStatus
from apps.classifiers.models import KOSGU, KVR
from apps.institutions.models import Institution


class RequestLineLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()
    line_description = serializers.CharField(source='line.description', read_only=True)

    class Meta:
        model = RequestLineLog
        fields = (
            'id', 'line', 'line_description',
            'old_amount', 'new_amount', 'comment',
            'changed_by', 'changed_by_name', 'changed_at',
        )

    def get_changed_by_name(self, obj) -> str:
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return ''


class RequestLineSerializer(serializers.ModelSerializer):
    kosgu_display = serializers.StringRelatedField(source='kosgu')
    kvr_display = serializers.StringRelatedField(source='kvr')
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = RequestLine
        fields = (
            'id', 'kosgu', 'kosgu_display', 'kvr', 'kvr_display',
            'description', 'unit_price', 'quantity', 'amount',
            'note', 'attachment', 'attachment_url',
        )
        read_only_fields = ('amount',)

    def get_attachment_url(self, obj) -> str | None:
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None


class RequestLineCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания строки заявки."""

    class Meta:
        model = RequestLine
        fields = (
            'id', 'kosgu', 'kvr', 'description',
            'unit_price', 'quantity', 'note', 'attachment',
        )

    def validate(self, attrs):
        if attrs.get('unit_price', 0) <= 0:
            raise serializers.ValidationError({'unit_price': 'Цена должна быть больше нуля.'})
        if attrs.get('quantity', 0) <= 0:
            raise serializers.ValidationError({'quantity': 'Количество должно быть больше нуля.'})
        return attrs


class BudgetRequestSerializer(serializers.ModelSerializer):
    lines = RequestLineSerializer(many=True, read_only=True)
    institution_name = serializers.StringRelatedField(source='institution')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    funding_type_display = serializers.CharField(source='get_funding_type_display', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BudgetRequest
        fields = (
            'id', 'institution', 'institution_name',
            'period_year', 'period_type', 'period_type_display',
            'period_quarter', 'funding_type', 'funding_type_display',
            'status', 'status_display',
            'total_amount', 'approved_amount',
            'created_at', 'submitted_at', 'reviewed_at', 'deadline',
            'comment', 'lines',
            'created_by', 'created_by_name',
            'reviewed_by', 'reviewed_by_name',
        )
        read_only_fields = (
            'total_amount', 'created_at', 'submitted_at', 'reviewed_at',
            'created_by', 'reviewed_by',
        )

    def get_reviewed_by_name(self, obj) -> str:
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name() or obj.reviewed_by.username
        return ''

    def get_created_by_name(self, obj) -> str:
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return ''


class BudgetRequestCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания новой заявки."""

    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = BudgetRequest
        fields = (
            'institution', 'period_year', 'period_type', 'period_quarter',
            'funding_type', 'deadline',
        )

    def validate(self, attrs):
        if attrs.get('period_type') == 'quarterly' and not attrs.get('period_quarter'):
            raise serializers.ValidationError(
                {'period_quarter': 'Необходимо указать квартал для квартальной заявки.'}
            )
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        institution = validated_data.get('institution')
        if not institution:
            try:
                institution = user.profile.institution
            except Exception:
                pass
        if not institution:
            raise serializers.ValidationError(
                {'institution': 'Укажите учреждение или привяжите его к профилю.'}
            )
        validated_data['institution'] = institution
        validated_data['created_by'] = user
        return super().create(validated_data)


class ReviewActionSerializer(serializers.Serializer):
    """Сериализатор для действия проверки заявки бухгалтером."""

    ACTION_CHOICES = [
        ('approve', 'Согласовать'),
        ('return', 'Вернуть на доработку'),
        ('reject', 'Отклонить'),
    ]

    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    approved_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True
    )
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        action = attrs.get('action')
        approved_amount = attrs.get('approved_amount')

        if action == 'approve' and not approved_amount:
            raise serializers.ValidationError(
                {'approved_amount': 'Необходимо указать согласованную сумму.'}
            )
        return attrs


class KOSGUSerializer(serializers.ModelSerializer):
    class Meta:
        model = KOSGU
        fields = ('id', 'code', 'name')


class KVRSerializer(serializers.ModelSerializer):
    class Meta:
        model = KVR
        fields = ('id', 'code', 'name')
