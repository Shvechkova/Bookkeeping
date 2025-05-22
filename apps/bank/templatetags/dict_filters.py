from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})
    # return ""

@register.filter
def get_month_by_name(months_list, month_name):
    for month in months_list:
        if month.get('name') == month_name:
            return month
    return {}
