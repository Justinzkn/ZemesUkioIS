from django import views
from django.urls import path
from .views import  apmoketi_visus, stripe_cancel, stripe_success, uzsakymas_atsaukti, uzsakymai_perziura, uzsakymas_redaguoti, uzsakymas_apmoketi, uzsakymas_naujas

urlpatterns = [
    path('', uzsakymai_perziura, name='uzsakymai'),
    path('naujas/', uzsakymas_naujas, name='uzsakymas_naujas'),
    path('redaguoti/<int:id>/', uzsakymas_redaguoti, name='uzsakymas_redaguoti'),
    path('apmoketi/<int:id>/', uzsakymas_apmoketi, name='uzsakymas_apmoketi'),
    path("atsaukti/<int:id>/", uzsakymas_atsaukti, name="uzsakymas_atsaukti"),
    path('apmoketi-visus/', apmoketi_visus, name='apmoketi_visus'),
    path('stripe/success/', stripe_success, name='stripe_success'),
    path('stripe/cancel/', stripe_cancel, name='stripe_cancel'),
]
