from django.core.validators import FileExtensionValidator
from django.db import models


class Anexo(models.Model):
    archivo = models.FileField(
        upload_to="anexos/", validators=[FileExtensionValidator(["pdf"]), valida_tamano]
    )
    nombre = models.CharField(max_length=80)
