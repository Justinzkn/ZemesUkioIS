from django.urls import path
from .views import  likuciu_zemelapis, preke_istrinti, preke_nauja, prekiu_sarasas, preke_perziura
from prekes.views import likuciu_zemelapis

urlpatterns = [
    path('', prekiu_sarasas, name='prekiu_sarasas'),
    path('<int:id>/', preke_perziura, name='preke_perziura'),
    path('nauja/', preke_nauja, name='preke_nauja'),
    path("istrinti/<int:id>/", preke_istrinti, name="preke_istrinti"),
    path("/likuciu_zemelapis/<int:preke_id>/", likuciu_zemelapis, name="likuciu_zemelapis"),
]