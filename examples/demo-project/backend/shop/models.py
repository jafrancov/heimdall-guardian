from django.db import models


class Order(models.Model):
    customer_email = models.CharField(max_length=200)
    total = models.DecimalField(max_digits=10, decimal_places=2)


class Invoice(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    document = models.FileField(upload_to="invoices/")
