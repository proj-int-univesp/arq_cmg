from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView

from .forms import CaixaDeArquivoForm, DocumentoForm, InteressadoForm
from .models import CaixaDeArquivo, Documento, Interessado

class MenuView(LoginRequiredMixin, TemplateView):
    template_name = 'arq_app/menu.html'

class CaixasdeArquivo(LoginRequiredMixin, ListView):
    model = CaixaDeArquivo
    template_name = 'arq_app/caixas.html'
    context_object_name = 'caixas'

class CaixaDetalhes(LoginRequiredMixin, TemplateView):
    template_name = 'arq_app/caixa_detalhes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caixa_id = self.kwargs.get('pk')
        caixa = CaixaDeArquivo.objects.get(pk=caixa_id)
        
        if caixa.documentos.exists():
            primeiro_documento = caixa.documentos.all().order_by('data_producao').first()
            ultimo_documento = caixa.documentos.all().order_by('data_producao').last()
            serie_documental = caixa.documentos.first().serie_documental
            data_inicial = primeiro_documento.data_producao
            data_final = ultimo_documento.data_producao
        else:
            serie_documental = None
            data_inicial = None
            data_final = None
            
        context['caixa'] = caixa
        context['serie_documental'] = serie_documental
        context['data_inicial'] = data_inicial
        context['data_final'] = data_final
        
        return context

class CaixaNova(LoginRequiredMixin, CreateView):
    form_class = CaixaDeArquivoForm
    template_name = 'arq_app/caixa_nova.html'
    success_url = '/arq-app/caixas/'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Caixa {form.instance} cadastrada com sucesso.")
        return response
    
class CaixaEditar(LoginRequiredMixin, UpdateView):
    model = CaixaDeArquivo
    form_class = CaixaDeArquivoForm
    template_name = 'arq_app/caixa_editar.html'
    success_url = '/arq-app/caixas/'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Caixa {self.object} editada com sucesso.")
        return response
    
class CaixaExcluir(LoginRequiredMixin, DeleteView):
    model = CaixaDeArquivo
    template_name = 'arq_app/caixa_excluir.html'
    success_url = '/arq-app/caixas/'
    
    def form_valid(self, form):

        messages.success(self.request, f"Caixa {self.object} excluída com sucesso.")
        return super(CaixaExcluir,self).form_valid(form)
    
class Documentos(LoginRequiredMixin, ListView):
    model = Documento
    template_name = 'arq_app/documentos.html'
    context_object_name = 'documentos'

class DocumentoDetalhes(LoginRequiredMixin, TemplateView):
    template_name = 'arq_app/documento_detalhes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documento_id = self.kwargs.get('pk')
        context['documento'] = Documento.objects.get(pk=documento_id)
        return context
    
class DocumentoEditar(LoginRequiredMixin, UpdateView):
    model = Documento
    form_class = DocumentoForm
    template_name = 'arq_app/documento_editar.html'
    success_url = '/arq-app/documentos/'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"O cadastro do documento {self.object} foi editado com sucesso.")
        return response

class DocumentoExcluir(LoginRequiredMixin, DeleteView):
    model = Documento
    template_name = 'arq_app/documento_excluir.html'
    success_url = '/arq-app/documentos/'
    
    def form_valid(self, form):

        messages.success(self.request, f"Documento {self.object} excluído com sucesso.")
        return super(DocumentoExcluir,self).form_valid(form)

class DocumentoNovo(LoginRequiredMixin, CreateView):
    form_class = DocumentoForm
    template_name = 'arq_app/documento_novo.html'
    success_url = '/arq-app/documentos/'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Documento {form.instance} cadastrado com sucesso.")
        return response

class Interessados(LoginRequiredMixin, ListView):
    model = Interessado
    template_name = 'arq_app/interessados.html'
    context_object_name = 'interessados'

class InteressadoNovo(LoginRequiredMixin, CreateView):
    form_class = InteressadoForm
    template_name = 'arq_app/interessado_novo.html'
    success_url = '/arq-app/interessados/'

    def form_valid(self, form):

        messages.success(self.request, f"Interessado {form.instance} cadastrado com sucesso.")
        return super(InteressadoNovo,self).form_valid(form)

class InteressadoEditar(LoginRequiredMixin, UpdateView):
    model = Interessado
    form_class = InteressadoForm
    template_name = 'arq_app/interessado_editar.html'
    success_url = '/arq-app/interessados/'

    def form_valid(self, form):

        messages.success(self.request, f"Interessado {self.object} editado com sucesso.")
        return super(InteressadoEditar,self).form_valid(form)

class InteressadoExcluir(LoginRequiredMixin, DeleteView):
    model = Interessado
    template_name = 'arq_app/interessado_excluir.html'
    success_url = '/arq-app/interessados/'
    
    def form_valid(self, form):

        messages.success(self.request, f"Interessado {self.object} excluído com sucesso.")
        return super(InteressadoExcluir,self).form_valid(form)