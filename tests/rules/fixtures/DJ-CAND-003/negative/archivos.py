import os


def descargar(request):
    ruta = os.path.join("/datos", "ayuda.txt")
    with open("/datos/ayuda.txt", "rb") as f:
        return f.read()


def configuracion():
    return open(os.path.join("/etc", "app.ini"))
