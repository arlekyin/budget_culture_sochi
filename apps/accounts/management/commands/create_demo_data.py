"""
Команда для создания полных демонстрационных данных.
Наполняет систему реалистичными данными для защиты диплома.
Запуск: python manage.py create_demo_data
"""

import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from apps.accounts.models import UserProfile, UserRole
from apps.institutions.models import Institution, InstitutionType, BudgetLimit
from apps.classifiers.models import KOSGU, KVR
from apps.budget_requests.models import (
    BudgetRequest, RequestLine, RequestLineLog,
    RequestStatus, PeriodType, FundingType,
)
from apps.monitoring.models import FactPayment, Reservation


# ---------------------------------------------------------------------------
# Справочники: КОСГУ (реальные коды Приказа Минфина № 209н)
# ---------------------------------------------------------------------------
KOSGU_DATA = [
    ('211', 'Заработная плата'),
    ('212', 'Прочие выплаты персоналу, за исключением ФОТ'),
    ('213', 'Начисления на выплаты по оплате труда (страховые взносы)'),
    ('221', 'Услуги связи'),
    ('222', 'Транспортные услуги'),
    ('223', 'Коммунальные услуги'),
    ('224', 'Арендная плата за пользование имуществом'),
    ('225', 'Работы, услуги по содержанию имущества'),
    ('226', 'Прочие работы и услуги'),
    ('228', 'Услуги, работы для целей капитальных вложений в объекты государственной (муниципальной) собственности'),
    ('261', 'Пенсии, пособия и выплаты по пенсионному, социальному и медицинскому страхованию населения'),
    ('266', 'Социальные пособия и компенсации персоналу в денежной форме'),
    ('267', 'Социальные компенсации персоналу в натуральной форме'),
    ('290', 'Прочие расходы'),
    ('291', 'Налоги, пошлины и сборы'),
    ('292', 'Штрафы за нарушение законодательства о налогах и сборах, законодательства о страховых взносах'),
    ('295', 'Другие экономические санкции'),
    ('296', 'Иные расходы'),
    ('310', 'Увеличение стоимости основных средств'),
    ('320', 'Увеличение стоимости нематериальных активов'),
    ('340', 'Увеличение стоимости материальных запасов'),
    ('341', 'Увеличение стоимости лекарственных препаратов и материалов, применяемых в медицинских целях'),
    ('343', 'Увеличение стоимости горюче-смазочных материалов'),
    ('344', 'Увеличение стоимости строительных материалов'),
    ('345', 'Увеличение стоимости мягкого инвентаря'),
    ('346', 'Увеличение стоимости прочих оборотных запасов (материалов)'),
    ('347', 'Увеличение стоимости материальных запасов для целей капитальных вложений'),
]

# ---------------------------------------------------------------------------
# Справочники: КВР (реальные коды Приказа Минфина № 82н / Указаний № 65н)
# ---------------------------------------------------------------------------
KVR_DATA = [
    ('111', 'Фонд оплаты труда учреждений'),
    ('112', 'Иные выплаты персоналу учреждений, за исключением фонда оплаты труда'),
    ('119', 'Взносы по обязательному социальному страхованию на выплаты по оплате труда работников и иные выплаты работникам учреждений'),
    ('121', 'Фонд оплаты труда государственных (муниципальных) органов'),
    ('122', 'Иные выплаты персоналу государственных (муниципальных) органов, за исключением фонда оплаты труда'),
    ('129', 'Взносы по обязательному социальному страхованию на выплаты по оплате труда и иные выплаты работникам государственных (муниципальных) органов'),
    ('211', 'Субсидии бюджетным учреждениям на финансовое обеспечение государственного (муниципального) задания на оказание государственных (муниципальных) услуг (выполнение работ)'),
    ('244', 'Прочая закупка товаров, работ и услуг'),
    ('311', 'Приобретение недвижимого имущества государственными (муниципальными) учреждениями'),
    ('321', 'Приобретение легковых автомобилей и мотоциклов'),
    ('323', 'Приобретение иных основных средств государственными (муниципальными) учреждениями'),
    ('340', 'Увеличение стоимости нематериальных активов учреждений'),
    ('852', 'Уплата прочих налогов, сборов'),
    ('853', 'Уплата иных платежей'),
]

# ---------------------------------------------------------------------------
# Учреждения культуры г. Сочи (реальные названия)
# ---------------------------------------------------------------------------
INSTITUTIONS_DATA = [
    {
        'short_name': 'МБУ «ЦБС г. Сочи»',
        'name': 'Муниципальное бюджетное учреждение «Централизованная библиотечная система города Сочи»',
        'institution_type': InstitutionType.LIBRARY,
        'inn': '2317034521',
        'address': 'г. Сочи, ул. Горького, 60',
        'head_name': 'Сидорова Елена Викторовна',
        'limit_2026': Decimal('42_500_000'),
        'limit_2025': Decimal('38_200_000'),
    },
    {
        'short_name': 'МБУК «Сочинский худ. музей»',
        'name': 'Муниципальное бюджетное учреждение культуры «Сочинский художественный музей»',
        'institution_type': InstitutionType.MUSEUM,
        'inn': '2317041872',
        'address': 'г. Сочи, ул. Советская, 30',
        'head_name': 'Козлов Иван Дмитриевич',
        'limit_2026': Decimal('26_800_000'),
        'limit_2025': Decimal('24_100_000'),
    },
    {
        'short_name': 'МБУДО «ДМШ №1 им. Сафонова»',
        'name': 'Муниципальное бюджетное учреждение дополнительного образования «Детская музыкальная школа №1 имени В.И. Сафонова»',
        'institution_type': InstitutionType.ART_SCHOOL,
        'inn': '2317028934',
        'address': 'г. Сочи, ул. Театральная, 8',
        'head_name': 'Новикова Ольга Петровна',
        'limit_2026': Decimal('31_600_000'),
        'limit_2025': Decimal('28_900_000'),
    },
    {
        'short_name': 'МБУДО «ДМШ №2»',
        'name': 'Муниципальное бюджетное учреждение дополнительного образования «Детская музыкальная школа №2»',
        'institution_type': InstitutionType.ART_SCHOOL,
        'inn': '2317031056',
        'address': 'г. Сочи, ул. Дагомысская, 42',
        'head_name': 'Воронова Татьяна Александровна',
        'limit_2026': Decimal('24_300_000'),
        'limit_2025': Decimal('22_700_000'),
    },
    {
        'short_name': 'МБУДО «ДХШ»',
        'name': 'Муниципальное бюджетное учреждение дополнительного образования «Детская художественная школа города Сочи»',
        'institution_type': InstitutionType.ART_SCHOOL,
        'inn': '2317045219',
        'address': 'г. Сочи, ул. Орджоникидзе, 15',
        'head_name': 'Малинина Светлана Юрьевна',
        'limit_2026': Decimal('17_900_000'),
        'limit_2025': Decimal('16_400_000'),
    },
    {
        'short_name': 'МБУК «ДК Центральный»',
        'name': 'Муниципальное бюджетное учреждение культуры «Дом культуры «Центральный» города Сочи»',
        'institution_type': InstitutionType.CULTURE_HOUSE,
        'inn': '2317052873',
        'address': 'г. Сочи, ул. Московская, 2',
        'head_name': 'Петренко Александр Николаевич',
        'limit_2026': Decimal('36_200_000'),
        'limit_2025': Decimal('33_800_000'),
    },
    {
        'short_name': 'МБУК «Молодёжный театр»',
        'name': 'Муниципальное бюджетное учреждение культуры «Сочинский молодёжный театр»',
        'institution_type': InstitutionType.THEATER,
        'inn': '2317019347',
        'address': 'г. Сочи, пл. Театральная, 1',
        'head_name': 'Романенко Дмитрий Сергеевич',
        'limit_2026': Decimal('54_100_000'),
        'limit_2025': Decimal('49_600_000'),
    },
    {
        'short_name': 'МБУК «Музей истории Сочи»',
        'name': 'Муниципальное бюджетное учреждение культуры «Музей истории города-курорта Сочи»',
        'institution_type': InstitutionType.MUSEUM,
        'inn': '2317063481',
        'address': 'г. Сочи, ул. Воровского, 54/11',
        'head_name': 'Захарова Наталья Игоревна',
        'limit_2026': Decimal('21_500_000'),
        'limit_2025': Decimal('19_800_000'),
    },
    {
        'short_name': 'МБУК «ГКЦ Сочи»',
        'name': 'Муниципальное бюджетное учреждение культуры «Городской культурный центр города Сочи»',
        'institution_type': InstitutionType.CULTURE_HOUSE,
        'inn': '2317077654',
        'address': 'г. Сочи, Курортный проспект, 32',
        'head_name': 'Белоусов Виктор Андреевич',
        'limit_2026': Decimal('33_700_000'),
        'limit_2025': Decimal('30_500_000'),
    },
]

# ---------------------------------------------------------------------------
# Пользователи
# ---------------------------------------------------------------------------
USERS_DATA = [
    # (username, password, first_name, last_name, role, inst_idx)
    ('admin',        'admin123',  'Администратор', 'Системы',   UserRole.ADMIN,      None),
    ('buh_ivanova',  'buh123',    'Мария',         'Иванова',   UserRole.ACCOUNTANT,  None),
    ('buh_sokolova', 'buh123',    'Анна',          'Соколова',  UserRole.ACCOUNTANT,  None),
    ('head_petrov',  'head123',   'Андрей',        'Петров',    UserRole.HEAD,        None),
    ('dir_library',  'dir123',    'Елена',         'Сидорова',  UserRole.DIRECTOR,    0),
    ('dir_museum',   'dir123',    'Иван',          'Козлов',    UserRole.DIRECTOR,    1),
    ('dir_dmsh1',    'dir123',    'Ольга',         'Новикова',  UserRole.DIRECTOR,    2),
    ('dir_dmsh2',    'dir123',    'Татьяна',       'Воронова',  UserRole.DIRECTOR,    3),
    ('dir_dhsh',     'dir123',    'Светлана',      'Малинина',  UserRole.DIRECTOR,    4),
    ('dir_dk',       'dir123',    'Александр',     'Петренко',  UserRole.DIRECTOR,    5),
    ('dir_theater',  'dir123',    'Дмитрий',       'Романенко', UserRole.DIRECTOR,    6),
    ('dir_hist',     'dir123',    'Наталья',       'Захарова',  UserRole.DIRECTOR,    7),
    ('dir_gkc',      'dir123',    'Виктор',        'Белоусов',  UserRole.DIRECTOR,    8),
]


class Command(BaseCommand):
    help = 'Создаёт полные демонстрационные данные для дипломной защиты'

    def handle(self, *args, **options) -> None:
        self._create_classifiers()
        admin_user = self._create_users()
        institutions = self._create_institutions(admin_user)
        self._create_requests(institutions, admin_user)
        self._create_fact_payments(institutions, admin_user)
        self._create_reservations(institutions, admin_user)
        self._print_summary()

    # ------------------------------------------------------------------
    def _create_classifiers(self) -> None:
        self.stdout.write('Создание классификаторов КОСГУ и КВР...')

        kosgu_count = 0
        for code, name in KOSGU_DATA:
            _, created = KOSGU.objects.get_or_create(
                code=code,
                defaults={'name': name, 'is_active': True},
            )
            if created:
                kosgu_count += 1

        kvr_count = 0
        for code, name in KVR_DATA:
            _, created = KVR.objects.get_or_create(
                code=code,
                defaults={'name': name, 'is_active': True},
            )
            if created:
                kvr_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'  КОСГУ: {KOSGU.objects.count()} записей '
            f'(новых: {kosgu_count}), '
            f'КВР: {KVR.objects.count()} записей (новых: {kvr_count})'
        ))

    # ------------------------------------------------------------------
    def _create_users(self) -> User:
        self.stdout.write('Создание пользователей...')
        for username, password, first_name, last_name, role, inst_idx in USERS_DATA:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_superuser': role == UserRole.ADMIN,
                    'is_staff': role in (UserRole.ADMIN, UserRole.ACCOUNTANT),
                },
            )
            if created:
                user.set_password(password)
                user.save()

        admin = User.objects.get(username='admin')
        self.stdout.write(self.style.SUCCESS(f'  Пользователей: {len(USERS_DATA)}'))
        return admin

    def _create_institutions(self, admin_user: User) -> list:
        self.stdout.write('Создание учреждений и лимитов...')
        institutions = []
        for data in INSTITUTIONS_DATA:
            inst, _ = Institution.objects.get_or_create(
                short_name=data['short_name'],
                defaults={
                    'name': data['name'],
                    'institution_type': data['institution_type'],
                    'inn': data['inn'],
                    'address': data['address'],
                    'head_name': data['head_name'],
                },
            )
            BudgetLimit.objects.get_or_create(
                institution=inst, year=2026,
                defaults={'total_limit': data['limit_2026'], 'set_by': admin_user},
            )
            BudgetLimit.objects.get_or_create(
                institution=inst, year=2025,
                defaults={'total_limit': data['limit_2025'], 'set_by': admin_user},
            )
            institutions.append(inst)

        # Привязываем профили пользователей к учреждениям
        for username, _, first_name, last_name, role, inst_idx in USERS_DATA:
            user = User.objects.get(username=username)
            institution = institutions[inst_idx] if inst_idx is not None else None
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'role': role, 'institution': institution},
            )

        self.stdout.write(self.style.SUCCESS(f'  Учреждений: {len(institutions)}'))
        return institutions

    # ------------------------------------------------------------------
    def _create_requests(self, institutions: list, admin_user: User) -> None:
        self.stdout.write('Создание бюджетных заявок...')
        buh = User.objects.get(username='buh_ivanova')
        count = 0

        # (inst_idx, status, year, funding_type, ratio, comment)
        scenarios = [
            # Включены в бюджет — прошлый год 2025
            (0, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('1.00'), ''),
            (1, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('0.96'), ''),
            (2, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('1.00'), ''),
            (3, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('0.93'), ''),
            (4, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('1.00'), ''),
            (5, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('0.98'), ''),
            (6, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('1.00'), ''),
            (7, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('0.95'), ''),
            (8, RequestStatus.INCLUDED, 2025, FundingType.SUBSIDY, Decimal('1.00'), ''),
            # Согласованы — текущий год 2026
            (0, RequestStatus.APPROVED, 2026, FundingType.SUBSIDY, Decimal('1.00'), ''),
            (1, RequestStatus.APPROVED, 2026, FundingType.SUBSIDY, Decimal('0.94'), ''),
            (2, RequestStatus.APPROVED, 2026, FundingType.SUBSIDY, Decimal('1.00'), ''),
            (5, RequestStatus.APPROVED, 2026, FundingType.SUBSIDY, Decimal('0.97'), ''),
            (6, RequestStatus.APPROVED, 2026, FundingType.SUBSIDY, Decimal('1.00'), ''),
            # Платные услуги — согласованы
            (2, RequestStatus.APPROVED, 2026, FundingType.PAID, Decimal('1.00'), ''),
            (3, RequestStatus.APPROVED, 2026, FundingType.PAID, Decimal('1.00'), ''),
            # На проверке (ожидают бухгалтера)
            (3, RequestStatus.SUBMITTED, 2026, FundingType.SUBSIDY, None, ''),
            (4, RequestStatus.SUBMITTED, 2026, FundingType.SUBSIDY, None, ''),
            (7, RequestStatus.SUBMITTED, 2026, FundingType.SUBSIDY, None, ''),
            (8, RequestStatus.SUBMITTED, 2026, FundingType.PAID,    None, ''),
            # Возвращены на доработку
            (4, RequestStatus.RETURNED, 2026, FundingType.SUBSIDY, None,
             'Необходимо приложить коммерческие предложения на закупку оборудования (строки 310). '
             'Сумма по статье 225 превышает норматив — обоснуйте.'),
            (7, RequestStatus.RETURNED, 2026, FundingType.OTHER,   None,
             'Статья 290 не обоснована. Укажите конкретное мероприятие и приложите смету расходов.'),
            # Черновики (ещё не отправлены)
            (5, RequestStatus.DRAFT, 2026, FundingType.SUBSIDY, None, ''),
            (8, RequestStatus.DRAFT, 2026, FundingType.SUBSIDY, None, ''),
        ]

        for (inst_idx, req_status, year, funding_type, ratio, comment) in scenarios:
            inst = institutions[inst_idx]
            director = User.objects.filter(
                profile__institution=inst, profile__role=UserRole.DIRECTOR
            ).first() or admin_user

            req = BudgetRequest.objects.create(
                institution=inst,
                period_year=year,
                period_type=PeriodType.ANNUAL,
                funding_type=funding_type,
                status=req_status,
                created_by=director,
                deadline=datetime.date(year, 11, 1),
                comment=comment,
            )

            lines = self._get_lines_for_institution(inst_idx, funding_type)
            for line_data in lines:
                kosgu = KOSGU.objects.filter(code=line_data['kosgu_code']).first()
                kvr = KVR.objects.filter(code=line_data['kvr_code']).first() if line_data.get('kvr_code') else None
                if not kosgu:
                    self.stderr.write(f'  КОСГУ {line_data["kosgu_code"]} не найден, пропуск строки')
                    continue
                RequestLine.objects.create(
                    request=req,
                    kosgu=kosgu,
                    kvr=kvr,
                    description=line_data['description'],
                    unit_price=Decimal(str(line_data['unit_price'])),
                    quantity=Decimal(str(line_data['quantity'])),
                )

            req.refresh_from_db()

            if req_status in (RequestStatus.APPROVED, RequestStatus.INCLUDED):
                req.submitted_at = timezone.now() - datetime.timedelta(days=30)
                req.reviewed_by = buh
                req.reviewed_at = timezone.now() - datetime.timedelta(days=20)
                req.approved_amount = (req.total_amount * ratio).quantize(Decimal('0.01'))
                req.save()
                if ratio < Decimal('1.00'):
                    for line in req.lines.all()[:1]:
                        RequestLineLog.objects.create(
                            line=line,
                            changed_by=buh,
                            old_amount=line.amount,
                            new_amount=(line.amount * ratio).quantize(Decimal('0.01')),
                            comment='Скорректировано в соответствии с доведёнными лимитами '
                                    'Департамента финансов администрации г. Сочи.',
                        )
            elif req_status == RequestStatus.SUBMITTED:
                req.submitted_at = timezone.now() - datetime.timedelta(days=3)
                req.save()
            elif req_status == RequestStatus.RETURNED:
                req.submitted_at = timezone.now() - datetime.timedelta(days=14)
                req.reviewed_by = buh
                req.reviewed_at = timezone.now() - datetime.timedelta(days=10)
                req.save()

            count += 1

        self.stdout.write(self.style.SUCCESS(f'  Заявок создано: {count}'))

    # ------------------------------------------------------------------
    def _get_lines_for_institution(self, inst_idx: int, funding_type: str) -> list:
        """Возвращает набор строк расходов для типа учреждения."""

        # Строки для заявок на платные услуги (расходы по внебюджетной деятельности)
        if funding_type == FundingType.PAID:
            return [
                {'kosgu_code': '221', 'kvr_code': '244',
                 'description': 'Услуги связи для обеспечения платной деятельности (интернет, телефон)',
                 'unit_price': 3_200, 'quantity': 12},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Рекламные услуги (объявления, баннеры, социальные сети)',
                 'unit_price': 18_500, 'quantity': 12},
                {'kosgu_code': '346', 'kvr_code': '244',
                 'description': 'Расходные материалы для платных занятий (бумага, краски, кисти, холсты)',
                 'unit_price': 12_400, 'quantity': 12},
                {'kosgu_code': '291', 'kvr_code': '244',
                 'description': 'Уплата налогов с доходов от приносящей доход деятельности',
                 'unit_price': 28_000, 'quantity': 4},
            ]

        # Базовые строки для всех учреждений (зарплата + коммуналка + связь)
        base = [
            {'kosgu_code': '211', 'kvr_code': '111',
             'description': 'Фонд оплаты труда работников учреждения на 2026 год',
             'unit_price': 1_650_000, 'quantity': 12},
            {'kosgu_code': '213', 'kvr_code': '119',
             'description': 'Начисления на выплаты по оплате труда (страховые взносы, тариф 30,2%)',
             'unit_price': 498_300, 'quantity': 12},
            {'kosgu_code': '221', 'kvr_code': '244',
             'description': 'Услуги телефонной связи (городская линия, 3 номера)',
             'unit_price': 1_850, 'quantity': 12},
            {'kosgu_code': '221', 'kvr_code': '244',
             'description': 'Услуги интернет-провайдера (тариф 100 Мбит/с)',
             'unit_price': 4_200, 'quantity': 12},
            {'kosgu_code': '223', 'kvr_code': '244',
             'description': 'Электроснабжение (тариф 5,23 руб/кВт·ч, норматив ~8 000 кВт·ч/мес.)',
             'unit_price': 41_840, 'quantity': 12},
            {'kosgu_code': '223', 'kvr_code': '244',
             'description': 'Теплоснабжение (отопительный сезон октябрь–апрель, 7 мес.)',
             'unit_price': 98_400, 'quantity': 7},
            {'kosgu_code': '223', 'kvr_code': '244',
             'description': 'Холодное водоснабжение и водоотведение',
             'unit_price': 7_620, 'quantity': 12},
            {'kosgu_code': '225', 'kvr_code': '244',
             'description': 'Техническое обслуживание систем вентиляции и кондиционирования (4 ТО в год)',
             'unit_price': 28_500, 'quantity': 4},
            {'kosgu_code': '291', 'kvr_code': '244',
             'description': 'Уплата налога на имущество организаций (авансовые платежи, 4 кв.)',
             'unit_price': 85_000, 'quantity': 4},
        ]

        # Специфичные строки по типу учреждения
        specific = {
            0: [  # ЦБС (библиотека)
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Подписка на периодические издания и доступ к базам данных (РИНЦ, e-Library)',
                 'unit_price': 124_500, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Услуги по оцифровке библиотечного фонда (договор с подрядчиком)',
                 'unit_price': 185_000, 'quantity': 1},
                {'kosgu_code': '340', 'kvr_code': '244',
                 'description': 'Приобретение книг и печатных изданий для пополнения фонда (420 экз.)',
                 'unit_price': 650, 'quantity': 420},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение стеллажей для книгохранилища (7 шт. × 18 500 руб.)',
                 'unit_price': 18_500, 'quantity': 7},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Текущий ремонт кровли главного корпуса (дефектная ведомость №12-2026)',
                 'unit_price': 347_000, 'quantity': 1},
            ],
            1: [  # Художественный музей
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Страхование экспонатов постоянной экспозиции (полис СПАО «Ингосстрах» на 2026 г.)',
                 'unit_price': 218_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Услуги охраны объекта (ЧОП «Щит», 24/7, договор №2026-01)',
                 'unit_price': 68_400, 'quantity': 12},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Текущий ремонт выставочного зала №3 (замена напольного покрытия, 180 м²)',
                 'unit_price': 420_000, 'quantity': 1},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение климатической витрины для хранения графических работ (1 шт.)',
                 'unit_price': 285_000, 'quantity': 1},
                {'kosgu_code': '346', 'kvr_code': '244',
                 'description': 'Расходные материалы для реставрационной мастерской (лаки, растворители, бумага)',
                 'unit_price': 12_400, 'quantity': 8},
            ],
            2: [  # ДМШ №1 им. Сафонова
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Настройка и техническое обслуживание 12 роялей и пианино (ИП Ткаченко В.Р.)',
                 'unit_price': 8_500, 'quantity': 12},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение цифрового пианино YAMAHA Clavinova CLP-785 (2 шт.)',
                 'unit_price': 198_000, 'quantity': 2},
                {'kosgu_code': '346', 'kvr_code': '244',
                 'description': 'Нотная литература и учебные пособия для учащихся (280 экз.)',
                 'unit_price': 850, 'quantity': 280},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Аренда концертного зала «Зимний театр» для проведения выпускных концертов',
                 'unit_price': 95_000, 'quantity': 2},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Услуги по охране труда, медицинские осмотры сотрудников (согл. ТК РФ)',
                 'unit_price': 28_700, 'quantity': 1},
            ],
            3: [  # ДМШ №2
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Техническое обслуживание и настройка 8 пианино (4 раза в год)',
                 'unit_price': 8_500, 'quantity': 8},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение скрипок 4/4 для оркестрового класса (6 инструментов)',
                 'unit_price': 24_500, 'quantity': 6},
                {'kosgu_code': '346', 'kvr_code': '244',
                 'description': 'Нотная литература и учебники по сольфеджио, муз. литературе',
                 'unit_price': 720, 'quantity': 180},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Организация и проведение городского конкурса юных музыкантов «Allegro»',
                 'unit_price': 78_000, 'quantity': 1},
            ],
            4: [  # ДХШ
                {'kosgu_code': '346', 'kvr_code': '244',
                 'description': 'Холсты грунтованные 60×80 см, масляные краски, кисти (набор для 240 учащихся)',
                 'unit_price': 1_850, 'quantity': 240},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Мольберты деревянные напольные для нового класса живописи (20 шт.)',
                 'unit_price': 4_200, 'quantity': 20},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Текущий ремонт скульптурной мастерской (штукатурка стен, покраска)',
                 'unit_price': 210_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Участие в межрегиональной выставке детского изобразительного искусства «Палитра»',
                 'unit_price': 42_500, 'quantity': 1},
            ],
            5: [  # ДК Центральный
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Организация и проведение городских культурно-массовых мероприятий (12 ед. в год)',
                 'unit_price': 145_000, 'quantity': 12},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Техническое обслуживание звукового и светового оборудования сцены',
                 'unit_price': 38_500, 'quantity': 12},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение цифрового микшерного пульта YAMAHA CL5 для главной сцены',
                 'unit_price': 685_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Пошив сценических костюмов для народного ансамбля «Кубань» (30 комплектов)',
                 'unit_price': 12_800, 'quantity': 30},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Замена театральных кресел в зрительном зале (150 шт. × 8 400 руб.)',
                 'unit_price': 8_400, 'quantity': 150},
            ],
            6: [  # Молодёжный театр
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Постановка нового спектакля «Дядя Ваня» (декорации, костюмы, реквизит)',
                 'unit_price': 1_850_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Гонорары приглашённых режиссёров и актёров (2 постановки в год)',
                 'unit_price': 380_000, 'quantity': 2},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Текущий ремонт гримёрных помещений (4 комнаты, штукатурка, сантехника)',
                 'unit_price': 285_000, 'quantity': 4},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение профессионального светодиодного оборудования для сцены',
                 'unit_price': 1_240_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Гастроли в рамках краевого театрального фестиваля «Кубань» (г. Краснодар)',
                 'unit_price': 245_000, 'quantity': 1},
            ],
            7: [  # Музей истории Сочи
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Разработка и монтаж новой интерактивной экспозиции «Сочи в годы Великой Отечественной»',
                 'unit_price': 980_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Услуги охраны объекта (ЧОП «Барьер», 24/7, договор №М-2026-02)',
                 'unit_price': 54_200, 'quantity': 12},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение мультимедийного проектора Epson EB-L1500UH (1 шт.)',
                 'unit_price': 384_000, 'quantity': 1},
                {'kosgu_code': '346', 'kvr_code': '244',
                 'description': 'Упаковочные и консервационные материалы для хранения музейных фондов',
                 'unit_price': 18_400, 'quantity': 6},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Реставрация фасада исторического здания (лицевая часть, 240 м²)',
                 'unit_price': 1_150_000, 'quantity': 1},
            ],
            8: [  # ГКЦ Сочи
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Организация городских культурно-массовых мероприятий (план 24 ед. в год)',
                 'unit_price': 185_000, 'quantity': 24},
                {'kosgu_code': '310', 'kvr_code': '244',
                 'description': 'Приобретение моноблоков Apple iMac 27" для медиастудии (5 шт.)',
                 'unit_price': 168_000, 'quantity': 5},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Полиграфические услуги (афиши А2, буклеты, программки к мероприятиям)',
                 'unit_price': 34_500, 'quantity': 12},
                {'kosgu_code': '225', 'kvr_code': '244',
                 'description': 'Текущий ремонт малого зала (шпаклёвка, покраска стен, замена освещения)',
                 'unit_price': 178_000, 'quantity': 1},
                {'kosgu_code': '226', 'kvr_code': '244',
                 'description': 'Услуги по техническому обеспечению городского фестиваля «Сочи-Арт 2026»',
                 'unit_price': 320_000, 'quantity': 1},
            ],
        }

        return base + specific.get(inst_idx, [])

    # ------------------------------------------------------------------
    def _create_fact_payments(self, institutions: list, admin_user: User) -> None:
        self.stdout.write('Создание кассовых расходов (факт)...')
        buh = User.objects.get(username='buh_ivanova')
        count = 0

        payments = [
            # (inst_idx, kosgu_code, amount, date, description, doc_number)
            # ЦБС — январь-апрель
            (0, '211', Decimal('18_400_000'), datetime.date(2026, 1, 15), 'Выплата заработной платы за январь 2026 г.', 'ПП-0124-01'),
            (0, '213', Decimal('5_556_800'),  datetime.date(2026, 1, 20), 'Страховые взносы за январь 2026 г. (ПФР, ФСС, ФОМС)', 'ПП-0125-01'),
            (0, '223', Decimal('412_600'),    datetime.date(2026, 1, 25), 'Оплата электроэнергии за январь 2026 (АО «Россети Кубань»)', 'ПП-0126-01'),
            (0, '223', Decimal('698_500'),    datetime.date(2026, 2, 10), 'Оплата теплоснабжения за февраль 2026 (МУП «Сочитеплоэнерго»)', 'ПП-0198-02'),
            (0, '211', Decimal('18_400_000'), datetime.date(2026, 2, 14), 'Выплата заработной платы за февраль 2026 г.', 'ПП-0199-02'),
            (0, '226', Decimal('124_500'),    datetime.date(2026, 3, 5),  'Оплата подписки на периодические издания (ООО «Пресса-Юг»)', 'ПП-0287-03'),
            (0, '211', Decimal('18_400_000'), datetime.date(2026, 3, 14), 'Выплата заработной платы за март 2026 г.', 'ПП-0312-03'),
            (0, '340', Decimal('273_000'),    datetime.date(2026, 4, 8),  'Приобретение книг для пополнения библиотечного фонда (420 экз.)', 'ПП-0401-04'),
            (0, '211', Decimal('18_400_000'), datetime.date(2026, 4, 15), 'Выплата заработной платы за апрель 2026 г.', 'ПП-0445-04'),
            # Художественный музей
            (1, '211', Decimal('10_200_000'), datetime.date(2026, 1, 15), 'Выплата заработной платы за январь 2026 г.', 'ПП-0130-01'),
            (1, '213', Decimal('3_080_400'),  datetime.date(2026, 1, 20), 'Страховые взносы за январь 2026 г.', 'ПП-0131-01'),
            (1, '223', Decimal('318_400'),    datetime.date(2026, 1, 24), 'Оплата электроэнергии за январь 2026 г.', 'ПП-0132-01'),
            (1, '226', Decimal('218_000'),    datetime.date(2026, 2, 3),  'Страхование музейных экспонатов на 2026 г. (СПАО «Ингосстрах»)', 'ПП-0201-02'),
            (1, '226', Decimal('68_400'),     datetime.date(2026, 2, 5),  'Оплата услуг охраны за февраль 2026 (ЧОП «Щит»)', 'ПП-0202-02'),
            (1, '211', Decimal('10_200_000'), datetime.date(2026, 2, 14), 'Выплата заработной платы за февраль 2026 г.', 'ПП-0210-02'),
            (1, '211', Decimal('10_200_000'), datetime.date(2026, 3, 14), 'Выплата заработной платы за март 2026 г.', 'ПП-0318-03'),
            (1, '211', Decimal('10_200_000'), datetime.date(2026, 4, 15), 'Выплата заработной платы за апрель 2026 г.', 'ПП-0421-04'),
            # ДМШ №1
            (2, '211', Decimal('14_200_000'), datetime.date(2026, 1, 15), 'Выплата заработной платы за январь 2026 г.', 'ПП-0140-01'),
            (2, '213', Decimal('4_288_400'),  datetime.date(2026, 1, 20), 'Страховые взносы за январь 2026 г.', 'ПП-0141-01'),
            (2, '225', Decimal('102_000'),    datetime.date(2026, 2, 18), 'Настройка 12 роялей и пианино (ИП Ткаченко В.Р.)', 'ПП-0225-02'),
            (2, '211', Decimal('14_200_000'), datetime.date(2026, 2, 14), 'Выплата заработной платы за февраль 2026 г.', 'ПП-0230-02'),
            (2, '310', Decimal('396_000'),    datetime.date(2026, 3, 22), 'Приобретение 2 цифровых пианино YAMAHA CLP-785 (ООО «МузТорг»)', 'ПП-0342-03'),
            (2, '211', Decimal('14_200_000'), datetime.date(2026, 3, 14), 'Выплата заработной платы за март 2026 г.', 'ПП-0360-03'),
            (2, '211', Decimal('14_200_000'), datetime.date(2026, 4, 15), 'Выплата заработной платы за апрель 2026 г.', 'ПП-0470-04'),
            # Молодёжный театр
            (6, '211', Decimal('22_800_000'), datetime.date(2026, 1, 15), 'Выплата заработной платы за январь 2026 г.', 'ПП-0170-01'),
            (6, '213', Decimal('6_885_600'),  datetime.date(2026, 1, 20), 'Страховые взносы за январь 2026 г.', 'ПП-0171-01'),
            (6, '226', Decimal('1_850_000'),  datetime.date(2026, 2, 28), 'Аванс (50%) по договору постановки «Дядя Ваня» (реж. Коваль А.Г.)', 'ПП-0265-02'),
            (6, '211', Decimal('22_800_000'), datetime.date(2026, 2, 14), 'Выплата заработной платы за февраль 2026 г.', 'ПП-0270-02'),
            (6, '211', Decimal('22_800_000'), datetime.date(2026, 3, 14), 'Выплата заработной платы за март 2026 г.', 'ПП-0380-03'),
            (6, '226', Decimal('380_000'),    datetime.date(2026, 4, 10), 'Гонорар приглашённых актёров (договор №2026-04-Г)', 'ПП-0450-04'),
            (6, '211', Decimal('22_800_000'), datetime.date(2026, 4, 15), 'Выплата заработной платы за апрель 2026 г.', 'ПП-0480-04'),
            # ДК Центральный
            (5, '211', Decimal('16_100_000'), datetime.date(2026, 1, 15), 'Выплата заработной платы за январь 2026 г.', 'ПП-0160-01'),
            (5, '213', Decimal('4_862_200'),  datetime.date(2026, 1, 20), 'Страховые взносы за январь 2026 г.', 'ПП-0161-01'),
            (5, '226', Decimal('145_000'),    datetime.date(2026, 2, 20), 'Проведение мероприятия «Масленица-2026» (смета №1)', 'ПП-0255-02'),
            (5, '211', Decimal('16_100_000'), datetime.date(2026, 2, 14), 'Выплата заработной платы за февраль 2026 г.', 'ПП-0260-02'),
            (5, '211', Decimal('16_100_000'), datetime.date(2026, 3, 14), 'Выплата заработной платы за март 2026 г.', 'ПП-0370-03'),
            (5, '211', Decimal('16_100_000'), datetime.date(2026, 4, 15), 'Выплата заработной платы за апрель 2026 г.', 'ПП-0460-04'),
        ]

        for (inst_idx, kosgu_code, amount, date, description, doc_num) in payments:
            kosgu = KOSGU.objects.filter(code=kosgu_code).first()
            if not kosgu:
                self.stderr.write(f'  КОСГУ {kosgu_code} не найден, пропуск платежа {doc_num}')
                continue
            FactPayment.objects.get_or_create(
                institution=institutions[inst_idx],
                document_number=doc_num,
                defaults={
                    'kosgu': kosgu,
                    'year': date.year,
                    'amount': amount,
                    'payment_date': date,
                    'description': description,
                    'added_by': buh,
                },
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'  Кассовых расходов: {count}'))

    # ------------------------------------------------------------------
    def _create_reservations(self, institutions: list, admin_user: User) -> None:
        self.stdout.write('Создание бронирований (договоры)...')
        buh = User.objects.get(username='buh_ivanova')
        count = 0

        reservations = [
            # (inst_idx, kosgu_code, contract_num, contractor, amount, date, status)
            (0, '225', '2026/КР-001', 'ООО «СтройПрофи»',          Decimal('347_000'),   datetime.date(2026, 3, 15), Reservation.ReservationStatus.ACTIVE),
            (0, '310', '2026/ОС-002', 'ООО «Офис-Мебель Сочи»',    Decimal('129_500'),   datetime.date(2026, 4, 1),  Reservation.ReservationStatus.ACTIVE),
            (1, '225', '2026/КР-003', 'ИП Василенко М.Г.',          Decimal('420_000'),   datetime.date(2026, 2, 20), Reservation.ReservationStatus.ACTIVE),
            (1, '310', '2026/ОС-004', 'ООО «КлиматТех»',            Decimal('285_000'),   datetime.date(2026, 4, 10), Reservation.ReservationStatus.ACTIVE),
            (2, '226', '2026/УС-005', 'МАУК «Зимний театр»',        Decimal('190_000'),   datetime.date(2026, 3, 10), Reservation.ReservationStatus.CLOSED),
            (2, '310', '2026/ОС-006', 'ООО «МузТорг»',              Decimal('396_000'),   datetime.date(2026, 3, 1),  Reservation.ReservationStatus.CLOSED),
            (5, '310', '2026/ОС-007', 'ООО «Аудио-Видео Юг»',       Decimal('685_000'),   datetime.date(2026, 4, 5),  Reservation.ReservationStatus.ACTIVE),
            (5, '226', '2026/УС-008', 'ИП Белоусова К.Д.',           Decimal('384_000'),   datetime.date(2026, 3, 25), Reservation.ReservationStatus.ACTIVE),
            (6, '226', '2026/УС-009', 'Коваль А.Г. (физ. лицо)',    Decimal('3_700_000'), datetime.date(2026, 1, 20), Reservation.ReservationStatus.ACTIVE),
            (6, '310', '2026/ОС-010', 'ООО «Свет-Сервис»',          Decimal('1_240_000'), datetime.date(2026, 4, 18), Reservation.ReservationStatus.ACTIVE),
            (7, '226', '2026/УС-011', 'ООО «ЭкспоДизайн»',          Decimal('980_000'),   datetime.date(2026, 2, 15), Reservation.ReservationStatus.ACTIVE),
            (7, '225', '2026/КР-012', 'ООО «РесторФасад»',          Decimal('1_150_000'), datetime.date(2026, 4, 22), Reservation.ReservationStatus.ACTIVE),
            (8, '226', '2026/УС-013', 'ООО «ПринтМастер»',          Decimal('414_000'),   datetime.date(2026, 3, 12), Reservation.ReservationStatus.ACTIVE),
            (8, '310', '2026/ОС-014', 'ООО «i-Store Краснодар»',    Decimal('840_000'),   datetime.date(2026, 4, 14), Reservation.ReservationStatus.ACTIVE),
        ]

        for (inst_idx, kosgu_code, contract_num, contractor, amount, date, status) in reservations:
            kosgu = KOSGU.objects.filter(code=kosgu_code).first()
            if not kosgu:
                self.stderr.write(f'  КОСГУ {kosgu_code} не найден, пропуск бронирования {contract_num}')
                continue
            Reservation.objects.get_or_create(
                institution=institutions[inst_idx],
                contract_number=contract_num,
                defaults={
                    'kosgu': kosgu,
                    'year': 2026,
                    'contractor': contractor,
                    'amount': amount,
                    'contract_date': date,
                    'status': status,
                    'created_by': buh,
                },
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'  Бронирований: {count}'))

    # ------------------------------------------------------------------
    def _print_summary(self) -> None:
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  Демо-данные успешно загружены!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('  Учётные записи для входа:')
        self.stdout.write('  ─────────────────────────────────────────────')
        self.stdout.write('  admin        / admin123  — Администратор системы')
        self.stdout.write('  buh_ivanova  / buh123    — Бухгалтер ЦБ (основной)')
        self.stdout.write('  buh_sokolova / buh123    — Бухгалтер ЦБ (второй)')
        self.stdout.write('  head_petrov  / head123   — Руководитель Упр. культуры')
        self.stdout.write('  dir_library  / dir123    — Директор МБУ «ЦБС»')
        self.stdout.write('  dir_museum   / dir123    — Директор МБУК «Худ. музей»')
        self.stdout.write('  dir_dmsh1    / dir123    — Директор МБУДО «ДМШ №1»')
        self.stdout.write('  dir_dmsh2    / dir123    — Директор МБУДО «ДМШ №2»')
        self.stdout.write('  dir_dhsh     / dir123    — Директор МБУДО «ДХШ»')
        self.stdout.write('  dir_dk       / dir123    — Директор МБУК «ДК Центральный»')
        self.stdout.write('  dir_theater  / dir123    — Директор МБУК «Молодёжный театр»')
        self.stdout.write('  dir_hist     / dir123    — Директор МБУК «Музей истории Сочи»')
        self.stdout.write('  dir_gkc      / dir123    — Директор МБУК «ГКЦ Сочи»')
        self.stdout.write('')
        self.stdout.write('  Статистика:')
        self.stdout.write(f'  КОСГУ: {KOSGU.objects.count()}, КВР: {KVR.objects.count()}')
        self.stdout.write(f'  Учреждений: {Institution.objects.count()}')
        self.stdout.write(f'  Бюджетных заявок: {BudgetRequest.objects.count()}')
        self.stdout.write(f'  Строк заявок: {RequestLine.objects.count()}')
        self.stdout.write(f'  Кассовых расходов: {FactPayment.objects.count()}')
        self.stdout.write(f'  Бронирований: {Reservation.objects.count()}')
        self.stdout.write('')
