"""
URL configuration for projektas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),
    path('paskyros/', TemplateView.as_view(template_name='paskyros.html')),
    path('grafiku_generavimas/', TemplateView.as_view(template_name='grafiku_generavimas.html')),
    path('grafikai/', TemplateView.as_view(template_name='grafikai.html')),
    path('pagrindinis/', TemplateView.as_view(template_name='pagrindinis.html')),
    path('uzsakymai/', TemplateView.as_view(template_name="uzsakymai.html")),
    path('naujas_uzsakymas/', TemplateView.as_view(template_name="naujas_uzsakymas.html")),
    path('algalapis/', TemplateView.as_view(template_name='algalapis.html')),
    path('redaguoti_uzsakyma/', TemplateView.as_view(template_name='redaguoti_uzsakyma.html')),
    path('apmoketi_uzsakyma/', TemplateView.as_view(template_name='apmoketi_uzsakyma.html')),
    path('registracija/', TemplateView.as_view(template_name='registracija.html')),
    path('prisijungimas/', TemplateView.as_view(template_name='prisijungimas.html')),
    path('prekiu_sarasas/', TemplateView.as_view(template_name='prekiu_sarasas.html')),
    path('preke/', TemplateView.as_view(template_name='preke_perziura.html')),
    path('preke_nauja/', TemplateView.as_view(template_name='preke_nauja.html')),
    path('likuciu_zemelapis/', TemplateView.as_view(template_name='likuciu_zemelapis.html'), name='likuciu_zemelapis'),
    path('uzklausos/', TemplateView.as_view(template_name='uzklausu_sarasas.html')),
    path('uzklausa_perziura/', TemplateView.as_view(template_name='uzklausa_perziura.html')),
    path('nauja_uzklausa/', TemplateView.as_view(template_name='nauja_uzklausa.html')),
    path('grafiko_keitimo_uzklausa/', TemplateView.as_view(template_name='grafiko_keitimo_uzklausa.html')),
    path('iranga/', TemplateView.as_view(template_name='irangos_perziura.html')),
    path('iranga_prideti/', TemplateView.as_view(template_name='iranga_prideti.html')),
    path('iranga_redaguoti/', TemplateView.as_view(template_name='iranga_redaguoti.html')),
    path('iranga_salinti/', TemplateView.as_view(template_name='iranga_salinti.html')),
    path('iranga_komplektavimas/', TemplateView.as_view(template_name='iranga_komplektavimas.html')),

]
