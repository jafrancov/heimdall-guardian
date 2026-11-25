import subprocess

from django.db import connection
from django.http import JsonResponse


def buscar(request):
    nombre = request.GET.get("nombre", "")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, nombre FROM usuarios WHERE nombre = '{nombre}'")
        filas = cursor.fetchall()
    return JsonResponse({"filas": filas})


def respaldo(request):
    destino = request.GET.get("destino", "/tmp/respaldo.sql")
    subprocess.call("pg_dump padron > " + destino, shell=True)
    return JsonResponse({"ok": True})
