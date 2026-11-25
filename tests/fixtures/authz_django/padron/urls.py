from django.urls import path

from . import views

urlpatterns = [
    path("", views.Lista.as_view()),
    path("nuevo/", views.Crear.as_view()),
    path("<int:pk>/borrar/", views.borrar),
    path("<int:pk>/editar/", views.editar),
    path("exportar/", views.exportar),
]
