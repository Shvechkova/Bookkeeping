from django import template
from apps.service.models import Service


register = template.Library()

@register.inclusion_tag('service/includes/service_menu.html')
def get_category_service():
    service = Service.objects.all()

    return {"service": service}