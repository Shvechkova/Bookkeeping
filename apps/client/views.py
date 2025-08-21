from django.shortcuts import render
from django.db.models import F, Q

from apps.client.models import Contract
from apps.service.models import Service
# Create your views here.
def clients(request):
    page_name = "clients"
    # куки для сортировки
    if request.COOKIES.get('sortClient') and request.COOKIES.get('sortClient') != "client":
        sort_сlient = request.COOKIES["sortClient"]
        contracts = Contract.objects.filter(
            Q(service__name=sort_сlient)).select_related(
            "client", "service", 'manager').order_by("service")
    else:
        sort_сlient = 'client'
        contracts = Contract.objects.all().select_related(
            "client", "service", 'manager').order_by("client")

    servise = Service.objects.all()

    title = "Клиенты"
    context = {
      
        "contracts": contracts,
        "title": title,
        "servise": servise,
        "page_name": page_name,
    }
    return render(request, "client/clients.html", context)

