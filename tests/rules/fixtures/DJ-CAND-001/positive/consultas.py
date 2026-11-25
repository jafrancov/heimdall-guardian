def buscar(cursor, tabla, nombre):
    cursor.execute(f"SELECT * FROM {tabla}")
    cursor.execute("SELECT * FROM clientes WHERE nombre = '%s'" % nombre)
    cursor.execute("SELECT * FROM " + tabla)
    Cliente.objects.raw("SELECT * FROM x WHERE n = '{}'".format(nombre))
