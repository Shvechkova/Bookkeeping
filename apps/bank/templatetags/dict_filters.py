from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return {}
    return dictionary.get(key, {})

@register.filter
def get_month_by_name(months, month_name):
    if months is None:
        return None
    for month in months:
        if month["name"] == month_name:
            return month
    return None

@register.filter
def items(dictionary):
    if dictionary is None:
        return []
    return dictionary.items()