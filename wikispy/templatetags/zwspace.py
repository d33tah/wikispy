from django.utils.safestring import mark_safe
from django import template

register = template.Library()
@register.filter(name='zwspace', is_safe=True)
def zwspace(value, arg):
    return mark_safe(value.replace(arg, arg + '&#x200B;'))
