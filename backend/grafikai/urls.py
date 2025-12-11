from django.urls import path
from .views import grafikas_perziura, grafiko_uzklausa_nauja, uzklausa_istrinti, uzklausa_nauja, uzklausos_sarasas, algalapis_generuoti

urlpatterns = [
    # /grafikai/
    path('', grafikas_perziura, name='grafikas_perziura'),
    path('uzklausa/', grafiko_uzklausa_nauja, name='grafiko_uzklausa_nauja'),
    path("uzklausos/", uzklausos_sarasas, name="uzklausos_sarasas"),
    path("uzklausos/nauja/", uzklausa_nauja, name="uzklausa_nauja"),
    path("uzklausos/istrinti/<int:id>/", uzklausa_istrinti, name="uzklausa_istrinti"),
    path("algalapis/", algalapis_generuoti, name="algalapis_generuoti"),
]