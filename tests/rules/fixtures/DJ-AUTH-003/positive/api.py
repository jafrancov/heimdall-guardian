from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


class Usuarios(viewsets.ModelViewSet):
    permission_classes = [AllowAny]


class Pagos(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)


@api_view(["POST"])
@permission_classes([AllowAny])
def importar(request):
    return None


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}
