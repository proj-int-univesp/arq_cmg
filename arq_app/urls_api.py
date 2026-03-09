from django.urls import path
from .views_api import CaixasPorSerieDocumentalAPIView, SerieDocumentalPCListAPIView

urlpatterns = [
    path('api/temporalidade/', SerieDocumentalPCListAPIView.as_view(), name='api-temporalidade'),
    path('api/caixas/serie/<str:codigo>/', CaixasPorSerieDocumentalAPIView.as_view(), name='api-caixas-por-serie')
]
