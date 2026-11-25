from django.views.decorators.csrf import csrf_protect


@csrf_protect
def notificar(request):
    return None
