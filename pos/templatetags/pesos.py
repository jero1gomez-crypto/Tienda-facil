from django import template
register = template.Library()

@register.filter
def pesos(v):
    return '$' + f'{int(v or 0):,}'.replace(',', '.')
