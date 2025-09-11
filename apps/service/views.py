from collections import defaultdict
import datetime
import itertools
from django.shortcuts import render
from django.core.cache import cache
from django.db.models.functions import TruncMonth
from django.db.models import Prefetch, OuterRef
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, F, OrderBy, Case, When, Value
from sql_util.utils import SubquerySum
from apps.service.models import (
    AdvPlatform,
    Service,
    ServicesClientMonthlyInvoice,
    SubcontractMonth,
)
from django.db.models.functions import Round
from project.settings import MONTHS_RU

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
    # sort_operation = "id"
    if request.COOKIES.get("sortOper"):
        sort_operation_op = request.COOKIES["sortOper"]
    else:
        sort_operation_op = "0"
        
 
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
            Prefetch("operation_set__bank_in"),
            Prefetch("operation_set__bank_to"),
            Prefetch("operation_set__suborder"),
            Prefetch("operation_set__suborder__category_employee"),
            Prefetch("operation_set__suborder__platform"),
        )
        .filter(service=category_service.id, month__year__gte=year, month__month__gte=old_month)
        .annotate(
            operation_amount_to_all=Sum(
                "operation__amount",
                filter=Q(operation__bank_in=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
                default=0,
            ),
            operation_amount_to_all_diff=F("contract_sum")
            - (F("operation_amount_to_all")),
            operation_amount_ooo=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=1)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_ooo_comment=(
                Count(
                    "operation__comment",
                    filter=Q(operation__bank_to=1)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                )
            ),
            operation_amount_ip=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=2)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_ip_comment=Count(
                "operation__comment",
                filter=Q(operation__bank_to=2)
                & Q(operation__bank_in=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
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
            operation_amount_nal_comment=(
                Count(
                    "operation__comment",
                    filter=Q(operation__bank_to=3)
                    & Q(operation__bank_in=5)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                )
            ),
        )
        .annotate(
            sum_subcontractmonth=SubquerySum("subcontractmonth__amount", default=0),
            target=(
                SubquerySum(
                    "subcontractmonth__amount",
                    filter=Q(platform__name="Таргет"),
                    default=0,
                )
            ),
            operation_amount_target_comment=Count(
                "operation__comment",
                filter=Q(operation__suborder__platform__name="Таргет")
                & Q(operation__bank_to=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
            ),
            yandex=(
                SubquerySum(
                    "subcontractmonth__amount",
                    filter=Q(platform__name="Я.Директ"),
                    default=0,
                )
            ),
            operation_amount_yandex_comment=Count(
                "operation__comment",
                filter=Q(operation__suborder__platform__name="Я.Директ")
                & Q(operation__bank_to=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
            ),
            employee_all=(
                SubquerySum(
                    "subcontractmonth__amount",
                    filter=Q(category_employee__isnull=False),
                    default=0,
                )
            ),
            operation_amount_employee_all_comment=Count(
                "operation__comment",
                filter=Q(operation__suborder__category_employee__isnull=False)
                & Q(operation__bank_to=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
            ),
        )
        .annotate(
            operation_amount_out_all=Sum(
                "operation__amount",
                filter=Q(operation__bank_to=5)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
                default=0,
            ),
            operation_amount_out_all_diff=F("diff_sum")
            - F("operation_amount_out_all"),
            operation_amount_out_all_diff_notnull=Case(
                        When(
                            operation_amount_out_all_diff=None,
                            then=("diff_sum"),
                        ),
                        When(
                            operation_amount_out_all_diff__isnull=False,
                            then=("operation_amount_out_all_diff"),
                        ),
                        
                    ),
            operation_amount_out_ooo=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=5)
                    & Q(operation__bank_in=1)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_out_ooo_comment=(
                Count(
                    "operation__comment",
                    filter=Q(operation__bank_to=5)
                    & Q(operation__bank_in=1)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                )
            ),
            operation_amount_out_ip=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=5)
                    & Q(operation__bank_in=2)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_out_ip_comment=Count(
                "operation__comment",
                filter=Q(operation__bank_to=5)
                & Q(operation__bank_in=2)
                & Q(operation__monthly_bill__id=OuterRef("pk")),
            ),
            operation_amount_out_nal=(
                Sum(
                    "operation__amount",
                    filter=Q(operation__bank_to=5)
                    & Q(operation__bank_in=3)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                    default=0,
                )
            ),
            operation_amount_out_nal_comment=(
                Count(
                    "operation__comment",
                    filter=Q(operation__bank_to=5)
                    & Q(operation__bank_in=3)
                    & Q(operation__monthly_bill__id=OuterRef("pk")),
                )
            ),
            operation_amount_out_all_diff_no_adv=F("sum_subcontractmonth") - F("operation_amount_out_all")
        
        )
        .annotate(
            operation_amount_out_all_and_storage=Sum(
                "operation__amount",
                filter=Q(operation__bank_to__in=[5, 4])
                & Q(operation__monthly_bill__id=OuterRef("pk")),
                default=0,
            ),
            operation_amount_storage_all=Sum(
                "operation__amount",
                filter=Q(operation__bank_to__in=[4])
                & Q(operation__monthly_bill__id=OuterRef("pk")),
                default=0,
            ),
            operation_amount_out_all_and_storage_diff=F("diff_sum")
            - (F("operation_amount_out_all_and_storage")),
        )
        .order_by("-month")
    )

    suborders = (
        SubcontractMonth.objects.select_related(
            "month_bill", "month_bill__service", "platform", "category_employee"
        )
        .prefetch_related()
        .filter(month_bill__service=category_service.id,month_bill__month__year__gte=year, month_bill__month__month__gte=old_month)
        
    )

    if title_name == "ADV":
        grouped = None
        suborders_name_employee = None
    else:
        suborders_name_employee = suborders.values_list('category_employee__name', flat=True).distinct()
        
        
        grouped=None
        grouped = defaultdict(list)
        total_suborders = defaultdict(list)
        for suborder in suborders:
            grouped[suborder.category_employee].append(suborder)
            total_suborders[suborder.category_employee].append(suborder)
        # for suborder in suborders:
        #     grouped[suborder.category_employee.name].append(suborder)
  

    service_month_invoice = itertools.groupby(
        service_month_invoice,
        lambda t: [
            MONTHS_RU[t.month.month - 1],
            t.month.strftime("%Y"),
        ],
    )

    # service_month_invoice = [
    #     (grouper, list(values)) for grouper, values in service_month_invoice

    # ]
    service_month_invoice_new = []
    for grouper, values in service_month_invoice:

        total = {
            "total_contract_sum": 0,
            "total_adv_all_sum": 0,
            "total_sum_subcontractmonth": 0,
            "total_sum_subcontractmonth_target": 0,
            "total_sum_subcontractmonth_yandex": 0,
            "total_sum_subcontractmonth_category_employee": 0,
            "total_operation_amount_to_all": 0,
            "total_operation_amount_to_all_diff": 0,
            "total_operation_amount_ooo": 0,
            "total_operation_amount_ip": 0,
            "total_operation_amount_nal": 0,
            "total_operation_amount_out_all_and_storage": 0,
            "total_operation_amount_storage_all": 0,
            "total_operation_amount_out_all_and_storage_diff": 0,
            "total_operation_amount_out_all": 0,
            "total_operation_amount_out_ooo": 0,
            "total_operation_amount_out_ip": 0,
            "total_operation_operation_amount_out_nal": 0,
            "total_sum_subcontractmonth_no_adv": 0,
            "total_operation_amount_out_all_diff_no_adv": 0,
        }
        val = list(values)
   
        if sort_operation_op == "1":
            val = sorted(
                    val,
                    key=lambda x:
                        x.operation_amount_to_all_diff,reverse=True
                )

        if sort_operation_op == "2":
            val = sorted(
                    val,
                    key=lambda x:
                        x.operation_amount_out_all_diff_notnull,reverse=True
                )
            
        
        
        
        for v in val:
            total["total_contract_sum"] = total["total_contract_sum"] + v.contract_sum
            total["total_adv_all_sum"] = total["total_adv_all_sum"] + v.adv_all_sum
            total["total_sum_subcontractmonth"] = (
                total["total_sum_subcontractmonth"] + v.diff_sum
            )
            if v.target:
                total["total_sum_subcontractmonth_target"] = (
                    total["total_sum_subcontractmonth_target"] + v.target
                )
            if v.yandex:
                total["total_sum_subcontractmonth_yandex"] = (
                    total["total_sum_subcontractmonth_yandex"] + v.yandex
                )
            if v.employee_all:
                total["total_sum_subcontractmonth_category_employee"] = (
                    total["total_sum_subcontractmonth_category_employee"]
                    + v.employee_all
                )

            total["total_operation_amount_to_all"] = (
                total["total_operation_amount_to_all"] + v.operation_amount_to_all
            )
            total["total_operation_amount_to_all_diff"] = (
                total["total_operation_amount_to_all_diff"]
                + v.operation_amount_to_all_diff
            )
            total["total_operation_amount_ooo"] = (
                total["total_operation_amount_ooo"] + v.operation_amount_ooo
            )
            total["total_operation_amount_ip"] = (
                total["total_operation_amount_ip"] + v.operation_amount_ip
            )
            total["total_operation_amount_nal"] = (
                total["total_operation_amount_nal"] + v.operation_amount_nal
            )

            total["total_operation_amount_out_all_and_storage"] = (
                total["total_operation_amount_out_all_and_storage"]
                + v.operation_amount_out_all_and_storage
            )
            total["total_operation_amount_storage_all"] = (
                total["total_operation_amount_storage_all"]
                + v.operation_amount_storage_all
            )
            if v.operation_amount_out_all_and_storage_diff:
                total["total_operation_amount_out_all_and_storage_diff"] = (
                    total["total_operation_amount_out_all_and_storage_diff"]
                    + v.operation_amount_out_all_and_storage_diff
                )

            total["total_operation_amount_out_all"] = (
                total["total_operation_amount_out_all"] + v.operation_amount_out_all
            )
            total["total_operation_amount_out_ooo"] = (
                total["total_operation_amount_out_ooo"] + v.operation_amount_out_ooo
            )
            total["total_operation_amount_out_ip"] = (
                total["total_operation_amount_out_ip"] + v.operation_amount_out_ip
            )
            total["total_operation_operation_amount_out_nal"] = (
                total["total_operation_operation_amount_out_nal"]
                + v.operation_amount_out_nal
            )
            if v.operation_amount_out_all_diff_no_adv:
                total["total_operation_amount_out_all_diff_no_adv"] = (
                    total["total_operation_amount_out_all_diff_no_adv"]
                    + v.operation_amount_out_all_diff_no_adv
                )
            if v.operation_amount_out_all_diff:
                total["total_sum_subcontractmonth_no_adv"] = (
                    total["total_sum_subcontractmonth_no_adv"]
                    + v.operation_amount_out_all_diff
                )

        item = [grouper, val, total]
        service_month_invoice_new.append(item)

    # все счета
    if title_name == "ADV":
        platform = AdvPlatform.objects.all()
    else:
        platform = None


    context = {
        "title": title,
        "service": service,
        "title_name": title_name,
        "type_url": type_url,
        "category_service": category_service,
        "now": now,
        "service_month_invoice": service_month_invoice_new,
        "platform": platform,
        "suborders": suborders,
        'grouped_suborders' : grouped,
        'suborders_name_employee': suborders_name_employee,
    }

    return render(request, "service/service_one.html", context)
