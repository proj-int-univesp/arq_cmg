from django.urls import path
from . import views

urlpatterns = [
    path('associar-termo-caixa/', views.associar_termo_caixa, name='associar_termo_caixa'),
]
