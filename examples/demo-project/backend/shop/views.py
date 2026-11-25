import subprocess

from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe

from shop.models import Order


def search_products(request):
    term = request.GET.get("q", "")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, name, price FROM products WHERE name LIKE '%{term}%'")
        rows = cursor.fetchall()
    return JsonResponse({"results": rows})


def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    return JsonResponse({"id": order.pk, "email": order.customer_email, "total": str(order.total)})


def export_orders(request):
    rows = Order.objects.values_list("id", "customer_email", "total")
    return JsonResponse({"orders": list(rows)})


def backup(request):
    target = request.GET.get("target", "/tmp/backup.sql")
    subprocess.call("pg_dump cornershop > " + target, shell=True)
    return JsonResponse({"ok": True})


def upload_invoice(request):
    order = Order.objects.get(pk=request.POST["order"])
    order.invoice_set.create(document=request.FILES["document"])
    return JsonResponse({"ok": True})


def greeting(request):
    name = request.GET.get("name", "friend")
    return HttpResponse(mark_safe("<h1>Welcome, " + name + "</h1>"))
