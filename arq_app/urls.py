from django.urls import path
from . import views

urlpatterns = [
    path('associar-termo-caixa/', views.associar_termo_caixa, name='associar_termo_caixa'),
    path('relatorio-eliminacao-pdf/', views.relatorio_eliminacao_pdf, name='relatorio_eliminacao_pdf'),
]
