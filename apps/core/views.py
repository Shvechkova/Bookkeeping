from django.shortcuts import render

# Create your views here.
def index(request):
    title = "Главная"
    context = {
        "title": title,

    }

    return render(request, "core/index.html", context)
