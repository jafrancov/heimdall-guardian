from django.db import connection


def buscar(nombre, orden):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM usuarios WHERE nombre = '{nombre}'")
        cursor.execute("SELECT * FROM usuarios WHERE nombre = '%s'" % nombre)
        cursor.execute("SELECT * FROM usuarios ORDER BY " + orden)
        cursor.execute("SELECT * FROM usuarios WHERE id = {}".format(nombre))
    return Usuario.objects.raw(f"SELECT * FROM usuarios WHERE nombre = '{nombre}'")
