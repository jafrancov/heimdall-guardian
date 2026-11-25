from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from padron import api, views
from padron.views import Detalle

router = DefaultRouter()
router.register("predios", api.PredioViewSet)
router.register("publico", api.CatalogoViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.inicio, name="inicio"),
    path("expedientes/", include("padron.urls")),
    path("detalle/<int:pk>/", Detalle.as_view()),
    path("reporte/", login_required(views.reporte)),
    path("api/", include(router.urls)),
    path("api/importar/", api.importar),
    path("api/estado/", api.estado),
]
