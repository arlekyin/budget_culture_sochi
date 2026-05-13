from django.utils import timezone

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.classifiers.models import KOSGU, KVR
from apps.accounts.models import UserRole

from .models import BudgetRequest, RequestLine, RequestLineLog, RequestStatus
from .serializers import (
    BudgetRequestSerializer,
    BudgetRequestCreateSerializer,
    RequestLineCreateSerializer,
    RequestLineLogSerializer,
    ReviewActionSerializer,
    KOSGUSerializer,
    KVRSerializer,
)


class BudgetRequestListAPI(ListAPIView):
    """GET /api/requests/ — список заявок с учётом роли пользователя."""

    serializer_class = BudgetRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            role = user.profile.role
        except Exception:
            return BudgetRequest.objects.none()

        qs = BudgetRequest.objects.select_related('institution', 'created_by', 'reviewed_by')

        if role == UserRole.DIRECTOR:
            qs = qs.filter(institution=user.profile.institution)

        # Фильтры из query params
        req_status = self.request.query_params.get('status')
        if req_status:
            qs = qs.filter(status=req_status)

        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(period_year=year)

        return qs.order_by('-created_at')


class BudgetRequestCreateAPI(APIView):
    """POST /api/requests/ — создать новую заявку."""

    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        try:
            role = request.user.profile.role
        except Exception:
            return Response({'detail': 'Профиль не найден.'}, status=404)

        if role != UserRole.DIRECTOR:
            return Response(
                {'detail': 'Только директор может создавать заявки.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BudgetRequestCreateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        out = BudgetRequestSerializer(obj, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class BudgetRequestDetailAPI(RetrieveAPIView):
    """GET /api/requests/:id/ — детальная заявка."""

    serializer_class = BudgetRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BudgetRequest.objects.prefetch_related(
            'lines__kosgu', 'lines__kvr'
        ).select_related('institution', 'created_by', 'reviewed_by')


class BudgetRequestSubmitAPI(APIView):
    """POST /api/requests/:id/submit/ — отправить заявку на проверку."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int) -> Response:
        try:
            obj = BudgetRequest.objects.get(pk=pk)
        except BudgetRequest.DoesNotExist:
            return Response({'detail': 'Заявка не найдена.'}, status=404)

        try:
            profile = request.user.profile
        except Exception:
            return Response({'detail': 'Профиль не найден.'}, status=404)

        if profile.role != UserRole.DIRECTOR:
            return Response(
                {'detail': 'Только директор может отправлять заявки.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.institution != profile.institution:
            return Response({'detail': 'Нет доступа к этой заявке.'}, status=403)

        if obj.status not in (RequestStatus.DRAFT, RequestStatus.RETURNED):
            return Response(
                {'detail': 'Заявку можно отправить только из статусов «Черновик» или «Возвращена».'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not obj.lines.exists():
            return Response(
                {'detail': 'Нельзя отправить пустую заявку.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not obj.check_limit():
            try:
                limit = obj.institution.limits.get(year=obj.period_year)
                over = obj.total_amount - limit.total_limit
                return Response(
                    {
                        'detail': (
                            f'Сумма заявки превышает установленный лимит на {over:,.2f} руб. '
                            f'(лимит: {limit.total_limit:,.2f} руб., заявлено: {obj.total_amount:,.2f} руб.). '
                            'Уменьшите сумму или обратитесь к бухгалтеру.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception:
                pass

        obj.status = RequestStatus.SUBMITTED
        obj.submitted_at = timezone.now()
        obj.save(update_fields=['status', 'submitted_at'])

        out = BudgetRequestSerializer(obj, context={'request': request})
        return Response(out.data)


class BudgetRequestReviewAPI(APIView):
    """POST /api/requests/:id/review/ — действие бухгалтера по заявке."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int) -> Response:
        try:
            obj = BudgetRequest.objects.get(pk=pk)
        except BudgetRequest.DoesNotExist:
            return Response({'detail': 'Заявка не найдена.'}, status=404)

        try:
            profile = request.user.profile
        except Exception:
            return Response({'detail': 'Профиль не найден.'}, status=404)

        if profile.role not in (UserRole.ACCOUNTANT, UserRole.ADMIN):
            return Response(
                {'detail': 'Только бухгалтер может проверять заявки.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.status != RequestStatus.SUBMITTED:
            return Response(
                {'detail': 'Заявка должна быть в статусе «На проверке».'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        action = data['action']
        obj.reviewed_by = request.user
        obj.reviewed_at = timezone.now()
        obj.comment = data.get('comment', '')

        if action == 'approve':
            obj.status = RequestStatus.APPROVED
            obj.approved_amount = data.get('approved_amount', obj.total_amount)
        elif action == 'return':
            obj.status = RequestStatus.RETURNED
        elif action == 'reject':
            obj.status = RequestStatus.REJECTED

        obj.save()

        out = BudgetRequestSerializer(obj, context={'request': request})
        return Response(out.data)


class RequestLineAddAPI(APIView):
    """POST /api/requests/:id/lines/ — добавить строку в заявку."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int) -> Response:
        try:
            obj = BudgetRequest.objects.get(pk=pk)
        except BudgetRequest.DoesNotExist:
            return Response({'detail': 'Заявка не найдена.'}, status=404)

        try:
            profile = request.user.profile
        except Exception:
            return Response({'detail': 'Профиль не найден.'}, status=404)

        if profile.role != UserRole.DIRECTOR:
            return Response(
                {'detail': 'Только директор может добавлять строки.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.institution != profile.institution:
            return Response({'detail': 'Нет доступа к этой заявке.'}, status=403)

        if obj.status not in (RequestStatus.DRAFT, RequestStatus.RETURNED):
            return Response(
                {'detail': 'Строки можно добавлять только в черновик или возвращённую заявку.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RequestLineCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        line = serializer.save(request=obj)

        from .serializers import RequestLineSerializer
        out = RequestLineSerializer(line, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)


class RequestLineDeleteAPI(APIView):
    """DELETE /api/requests/:id/lines/:line_id/ — удалить строку заявки."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk: int, line_id: int) -> Response:
        try:
            obj = BudgetRequest.objects.get(pk=pk)
        except BudgetRequest.DoesNotExist:
            return Response({'detail': 'Заявка не найдена.'}, status=404)

        try:
            profile = request.user.profile
        except Exception:
            return Response({'detail': 'Профиль не найден.'}, status=404)

        if profile.role != UserRole.DIRECTOR:
            return Response(
                {'detail': 'Только директор может удалять строки.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if obj.institution != profile.institution:
            return Response({'detail': 'Нет доступа к этой заявке.'}, status=403)

        if obj.status not in (RequestStatus.DRAFT, RequestStatus.RETURNED):
            return Response(
                {'detail': 'Строки можно удалять только из черновика или возвращённой заявки.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            line = obj.lines.get(pk=line_id)
        except RequestLine.DoesNotExist:
            return Response({'detail': 'Строка не найдена.'}, status=404)

        line.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestLineLogsAPI(ListAPIView):
    """GET /api/requests/:id/logs/ — история изменений строк заявки."""

    serializer_class = RequestLineLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return RequestLineLog.objects.filter(
            line__request_id=pk
        ).select_related('line', 'changed_by').order_by('-changed_at')


class KOSGUListAPI(ListAPIView):
    """GET /api/classifiers/kosgu/ — справочник КОСГУ."""

    serializer_class = KOSGUSerializer
    permission_classes = [IsAuthenticated]
    queryset = KOSGU.objects.filter(is_active=True)


class KVRListAPI(ListAPIView):
    """GET /api/classifiers/kvr/ — справочник КВР."""

    serializer_class = KVRSerializer
    permission_classes = [IsAuthenticated]
    queryset = KVR.objects.filter(is_active=True)
