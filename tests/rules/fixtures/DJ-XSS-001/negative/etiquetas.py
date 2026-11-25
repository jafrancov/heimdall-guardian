from django.utils.html import format_html
from django.utils.safestring import mark_safe


def saludo(nombre):
    return format_html("<b>{}</b>", nombre)


def separador():
    return mark_safe("<hr>")
