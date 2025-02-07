from django import template

register = template.Library()

@register.filter
def first_word(value):
    if isinstance(value, str):
        return value.split(" ")[0]
    return value