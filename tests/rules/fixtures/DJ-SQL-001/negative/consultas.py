from django.db import connection


def buscar(nombre):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", [nombre])
        cursor.execute("SELECT count(*) FROM usuarios")
    return Usuario.objects.raw("SELECT * FROM usuarios WHERE nombre = %s", [nombre])
