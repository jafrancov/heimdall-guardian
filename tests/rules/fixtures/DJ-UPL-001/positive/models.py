from django.db import models


class Anexo(models.Model):
    archivo = models.FileField(upload_to="anexos/")
