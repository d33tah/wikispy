from django.utils.safestring import mark_safe
from django import template

register = template.Library()
@register.filter
def subtract(value, arg):
    """A filter that returns an expression reduced by the argument. Meant for
       situations like: "offset|subtract:pagesize", where "offset|add:pagesize"
       would not be possible."""
    return value - arg
