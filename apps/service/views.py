import datetime
import itertools
from django.shortcuts import render
from django.core.cache import cache
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value

from apps.service.models import (
    AdvPlatform,
    Service,
    ServicesClientMonthlyInvoice,
    SubcontractMonth,
)


# Create your views here.
def service_all(request):
    title = "Услуги"
    context = {
        "title": title,
    }
    return render(request, "service/service_all.html", context)


def service_one(request, slug):
    import locale

    locale.setlocale(locale.LC_ALL, "")

    category_service = Service.objects.get(name=slug)
    type_url = "service"
    title = category_service.id
    title_name = category_service.name

    # locale.setlocale(locale.LC_ALL, "russian")
    # общая функция кешировани
    def loc_mem_cache(key, function, timeout=300):
        cache_data = cache.get(key)
        if not cache_data:
            cache_data = function()
            cache.set(key, cache_data, timeout)
        return cache_data

    # все сервисы
    def service_cache():
        def cache_function():
            service = Service.objects.all()
            return service

        return loc_mem_cache("service", cache_function, 200)

    service = service_cache()

    # куки для установки дат сортировки
    if request.COOKIES.get("sortMonth"):
        month = request.COOKIES["sortMonth"]
    else:
        month = "1"

    # куки для установки сортировки operation
    sort_operation = "id"

    if request.COOKIES.get("sortOper"):
        sort_operation_op = request.COOKIES["sortOper"]
        if sort_operation_op == "1":
            sort_operation = "chekin_sum_entrees"

        if sort_operation_op == "2":
            sort_operation = "chekin_sum_adv"

    now = datetime.datetime.now()
    year = now.year

    # выбор периода сортировки
    if month == "1":
        old_month = now.month

    elif month == "2":
        old_month = now.month - 1
        if old_month == 0:
            old_month = 12
        year = now.year
        if old_month == 12:
            year = year - 1
    elif month == "3":
        old_month = now.month - 2
        if old_month == 0:
            old_month = 12
        year = now.year
        if old_month == 12:
            year = year - 1
    elif month == "12":
        old_month = 1
        year = now.year
    elif month == "999":
        old_month = 1
        year = 1990

    service_month_invoice = (
        ServicesClientMonthlyInvoice.objects.select_related(
            "client", "service", "contract"
        )
        .prefetch_related(
            Prefetch("subcontractmonth_set"),
            Prefetch("subcontractmonth_set__platform"),
            Prefetch("subcontractmonth_set__category_employee"),
            Prefetch("operation_set"),
        )
        .filter(service=category_service.id)
        .annotate(
            operation_amount_to_all=Sum(
                "operation__amount",
                filter=Q(operation__bank_in=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
                default=0,
            ),
            operation_amount_ip=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=1)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_ip_comment=Case(
                When(
                    operation__comment=F("operation__comment"), then="operation__comment"
                )
            ),
            operation_amount_ooo=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=2)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_nal=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=3)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
        )
        .annotate(
            operation_amount_to_all_diff=F("contract_sum")
            - (F("operation_amount_to_all")),
        )
        # .annotate(
        #     amount_sum_subs=Sum("subcontractmonth__amount", default=0),
        #     target=(
        #         Sum(
        #             "subcontractmonth__amount",
        #             filter=Q(subcontractmonth__platform__name="Таргет"),
        #             default=0,
        #         )
        #     ),
        #     yandex=(
        #         Sum(
        #             "subcontractmonth__amount",
        #             filter=Q(subcontractmonth__platform__name="Я.Директ"),
        #             default=0,
        #         )
        #     ),
        #     employee_all=(
        #         Sum(
        #             "subcontractmonth__amount",
        #             filter=Q(subcontractmonth__category_employee__isnull=False),
        #             default=0,
        #         )
        #     ),
        # )
        .annotate(
            sum_subcontractmonth=Sum("subcontractmonth__amount"),
        )
        # .values(
        #     "subcontractmonth__month_bill",
        #     "subcontractmonth__month_bill_id",
        #     "subcontractmonth__platform",
        #     "subcontractmonth__category_employee",
        # )
        # .annotate(
        #     amount_sum=(Sum("subcontractmonth__amount", default=0)),
        # )
        .order_by("-month")
    )
    for service_month_invoice_p in service_month_invoice:
        print(service_month_invoice_p)
        print(service_month_invoice_p.operation_amount_to_all)
    # subcontract_month_item = service_month_invoice.values(
    #     "id",
    #     "subcontractmonth__month_bill",
    #     "subcontractmonth__month_bill_id",
    #     "subcontractmonth__category_employee",
    #     "subcontractmonth__category_employee__name",
    #     "subcontractmonth__platform",
    #     "subcontractmonth__platform__name",
    # ).annotate(
    #     amount_sum=(Sum("subcontractmonth__amount", default=0)),
    # )
    service_month_invoice = service_month_invoice.annotate(
        amount_sum_subs=Sum("subcontractmonth__amount", default=0),
        target=(
            Sum(
                "subcontractmonth__amount",
                filter=Q(subcontractmonth__platform__name="Таргет"),
                default=0,
            )
        ),
        yandex=(
            Sum(
                "subcontractmonth__amount",
                filter=Q(subcontractmonth__platform__name="Я.Директ"),
                default=0,
            )
        ),
        employee_all=(
            Sum(
                "subcontractmonth__amount",
                filter=Q(subcontractmonth__category_employee__isnull=False),
                default=0,
            )
        ),
    )

    import pymorphy3

    morph = pymorphy3.MorphAnalyzer(lang="ru")

    service_month_invoice = itertools.groupby(
        service_month_invoice,
        lambda t: [
            morph.parse(t.month.strftime("%B"))[0].normal_form.title(),
            t.month.strftime("%Y"),
        ],
    )

    service_month_invoice = [
        (grouper, list(values)) for grouper, values in service_month_invoice
    ]
    print(service_month_invoice)
    # все счета
    if title_name == "ADV":
        platform = AdvPlatform.objects.all()
    else:
        platform = None

    print(platform)

    context = {
        "title": title,
        "service": service,
        "title_name": title_name,
        "type_url": type_url,
        "category_service": category_service,
        # "bills": bill_now_mohth,
        "now": now,
        # "suborders_name": suborders_name,
        # "obj_suborder_adv": obj_suborder_adv,
        # "suborders_name_no_adv": suborders_name_no_adv,
        # "operation": operation,
        # "total_month": total_month,
        # "diff_sum_oper": diff_sum_oper,
        # "obj_suborder_other": obj_suborder_other,
        # "bill_now_mohth_name": bill_now_mohth_name,
        # "bill_month": bill_month
        "service_month_invoice": service_month_invoice,
        "platform": platform,
        # "subcontract_month_item": subcontract_month_item,
    }

    return render(request, "service/service_one.html", context)
