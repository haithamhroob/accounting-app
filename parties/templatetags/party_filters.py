from django import template

register = template.Library()

@register.filter(name='abs')
def abs_filter(value):
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value
