from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


class PredioViewSet(viewsets.ModelViewSet):
    queryset = None


class CatalogoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]


@api_view(["POST"])
@permission_classes([AllowAny])
def importar(request):
    return None


@api_view(["GET"])
def estado(request):
    return None
