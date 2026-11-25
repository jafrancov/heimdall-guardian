from django.utils import safestring
from django.utils.safestring import mark_safe


def saludo(nombre):
    return mark_safe("<b>" + nombre + "</b>")


def aviso(texto):
    return safestring.mark_safe(texto)
