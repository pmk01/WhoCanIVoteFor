from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter(name='ni_postcode')
@stringfilter
def ni_postcode(postcode):
    if re.match('^BT.*', postcode):
        return True
