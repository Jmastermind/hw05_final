from django import forms, template
from django.utils.safestring import SafeText

register = template.Library()


@register.filter
def addclass(field: forms.BoundField, css: SafeText) -> SafeText:
    return field.as_widget(attrs={'class': css})
