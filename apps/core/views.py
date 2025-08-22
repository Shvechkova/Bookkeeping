import datetime
from functools import cache
from django.shortcuts import render

from apps.service.models import ServicesClientMonthlyInvoice, SubcontractMonth

# Create your views here.
def index(request):
    title = "Главная"
    context = {
        "title": title,

    }

    return render(request, "core/index.html", context)

def cache_delete(request):

    from django.core.cache import cache

    cache.delete("bank_1_context_2025")
    cache.clear()

    title = "cache_delete"
    context = {
        "title": title,

    }
    return render(request, "core/index.html", context)
    
def test(request):
    title = "TEST"

    now = datetime.datetime.now()

    old_month = now.month - 1
    if old_month == 0:
        old_month = 12
    year = now.year
    if old_month == 12:
        year = year - 1

    bill_now_old = ServicesClientMonthlyInvoice.objects.filter(
        month__year=year, month__month=old_month)

    for old_bill in bill_now_old:
        subcontr_old = SubcontractMonth.objects.filter(month_bill=old_bill.id)

        new_bill = old_bill
        new_bill.pk = None
        new_bill.month = now
        new_bill.operations_add_all = 0
        new_bill.operations_add_diff_all = old_bill.operations_add_all

        new_bill.save()
        if subcontr_old.exists():
            for subs_old in subcontr_old:

                new_subs = subs_old
                new_subs.pk = None
                new_subs.month_bill_id = new_bill.id

                new_subs.save()
    
    
    context = {
        "title": title,

    }

    return render(request, "core/test_item.html", context)
