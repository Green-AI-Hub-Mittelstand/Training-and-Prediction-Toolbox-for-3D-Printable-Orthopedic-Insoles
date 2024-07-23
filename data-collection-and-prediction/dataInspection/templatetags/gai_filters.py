

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def visualize_boolean(value):
    if value:
        return mark_safe('<span style="color: green; font-size: 1.2em;">&#10003;</span>')  # Checkmark
    else:
        return mark_safe('<span style="color: red; font-size: 1.2em;">&#10008;</span>')  # Cross
