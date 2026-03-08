"""
URL configuration for arq_cmg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from arq_app import views

urlpatterns = [
    path('', views.MenuView.as_view(), name='menu'),

    path('arq-app/caixas/', views.CaixasdeArquivo.as_view(), name='caixas'),
    path('arq-app/caixa/detalhes/<int:pk>/', views.CaixaDetalhes.as_view(), name='detalhes_caixa'),
    path('arq-app/caixa/nova/', views.CaixaNova.as_view(), name='nova_caixa'),
    path('arq-app/caixa/editar/<int:pk>/', views.CaixaEditar.as_view(), name='editar_caixa'),
    path('arq-app/caixa/excluir/<int:pk>/', views.CaixaExcluir.as_view(), name='excluir_caixa'),
    path('arq-app/documentos/', views.Documentos.as_view(), name='documentos'),
    path('arq-app/documento/detalhes/<int:pk>/', views.DocumentoDetalhes.as_view(), name='detalhes_documento'),
    path('arq-app/documento/novo/', views.DocumentoNovo.as_view(), name='novo_documento'),
    path('arq-app/documento/editar/<int:pk>/', views.DocumentoEditar.as_view(), name='editar_documento'),
    path('arq-app/documento/excluir/<int:pk>/', views.DocumentoExcluir.as_view(), name='excluir_documento'),
    path('arq-app/interessados/', views.Interessados.as_view(), name='interessados'),
    path('arq-app/interessado/novo', views.InteressadoNovo.as_view(), name='novo_interessado'),
    path('arq-app/interessado/editar/<int:pk>/', views.InteressadoEditar.as_view(), name='editar_interessado'),
    path('arq-app/interessado/excluir/<int:pk>/', views.InteressadoExcluir.as_view(), name='excluir_interessado'),
    path('arq-app/', include('arq_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Gerenciamento SisCA"
admin.site.site_title = "SisCA Admin"
admin.site.index_title = "Sistema de Controle de Arquivo"
