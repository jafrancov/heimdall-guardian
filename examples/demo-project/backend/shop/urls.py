from django.contrib.auth.decorators import login_required
from django.urls import path

from shop import views

urlpatterns = [
    path("products/search/", views.search_products),
    path("orders/<int:pk>/", views.order_detail),
    path("orders/export/", login_required(views.export_orders)),
    path("backup/", views.backup),
    path("invoices/upload/", views.upload_invoice),
    path("greeting/", views.greeting),
]
