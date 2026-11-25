from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def notificar(request):
    return None


@method_decorator(csrf_exempt, name="dispatch")
class Recibir(View):
    pass


urlpatterns = [path("hook/", csrf_exempt(notificar))]
