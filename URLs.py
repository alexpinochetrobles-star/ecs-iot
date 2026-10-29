from django.urls import path
from . import views

urlpatterns = [
    path("",                    views.dashboard,              name="dashboard"),
    path("api/lecturas/",       views.api_ultimas_lecturas,   name="api_lecturas"),
    path("api/estado-gpio/",    views.api_estado_gpio,        name="api_estado_gpio"),
    path("api/bomba/",          views.api_controlar_bomba,    name="api_bomba"),
]