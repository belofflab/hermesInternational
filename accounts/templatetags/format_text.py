from django import template

register = template.Library()


@register.filter("minimalize")
def minimalize(value):
    return value[:15]