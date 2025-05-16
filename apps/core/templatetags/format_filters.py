from django import template

register = template.Library()

@register.filter
def format_rub(value):
    if value == None:
        return f"0"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    if value == int(value):
        # val =  "{0}".format(value)
        value = int(value)
        value = '{0:,}'.format(value).replace(',', ' ')
        return f"{value}"
    
    
    val = "{0:,.2f}".format(value).replace(",", " ")
    return f"{val}"
    # return f"{value:.2f}"