from django.urls import path
from .views import  iranga_iskomplektuoti, irangos_perziura, iranga_prideti, iranga_redaguoti, iranga_salinti, iranga_komplektavimas

urlpatterns = [
    path('', irangos_perziura, name='iranga'),
    path('prideti/', iranga_prideti, name='iranga_prideti'),
    path('redaguoti/<int:id>/', iranga_redaguoti, name='iranga_redaguoti'),
    path('salinti/<int:id>/', iranga_salinti, name='iranga_salinti'),
    path('komplektavimas/', iranga_komplektavimas, name='iranga_komplektavimas'),
    path('iskomplektuoti/<int:id>/', iranga_iskomplektuoti, name='iranga_iskomplektuoti'),

]
