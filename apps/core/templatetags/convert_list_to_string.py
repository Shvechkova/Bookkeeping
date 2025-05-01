from django import template

import json

register = template.Library()

@register.filter(name='convert_list_to_string')
def convert_list_to_string(value):
   data = json.loads(value) # convert string to list
   return ', '.join([e for e in data]) # create a string and return