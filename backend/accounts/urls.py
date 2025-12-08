from django.urls import path
from .views import registracija, prisijungimas, atsijungti

urlpatterns = [
    path("registracija/", registracija, name="registracija"),
    path("prisijungimas/", prisijungimas, name="prisijungimas"),
    path("atsijungti/", atsijungti, name="atsijungti"),
]