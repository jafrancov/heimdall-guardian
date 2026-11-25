def buscar(cursor, nombre):
    cursor.execute("SELECT * FROM clientes WHERE nombre = %s", [nombre])
    cursor.execute("SELECT * FROM clientes")
    Cliente.objects.raw("SELECT * FROM x WHERE n = %s", [nombre])
