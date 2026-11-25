import os


def descargar(request, nombre):
    ruta = os.path.join("/datos", nombre)
    return open(ruta, "rb")


def ver(request):
    return open(request.GET["f"])
