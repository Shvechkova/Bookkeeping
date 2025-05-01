import datetime
import itertools
from django.shortcuts import render
from django.core.cache import cache
from django.db.models.functions import TruncMonth


from apps.service.models import Service, ServicesClientMonthlyInvoice


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
        ServicesClientMonthlyInvoice.objects.all()
        .select_related("client", "service", "contract")
        .prefetch_related()
        .order_by("-month")
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
    category_service = Service.objects.get(name=slug)
    type_url = "service"
    title = category_service.id
    title_name = category_service.name
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
    }

    return render(request, "service/service_one.html", context)
