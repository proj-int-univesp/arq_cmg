from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView

from .forms import CaixaDeArquivoForm, InteressadoForm
from .models import CaixaDeArquivo, Interessado

class MenuView(LoginRequiredMixin, TemplateView):
    template_name = 'arq_app/menu.html'

class CaixasdeArquivo(LoginRequiredMixin, ListView):
    model = CaixaDeArquivo
    template_name = 'arq_app/caixas.html'
    context_object_name = 'caixas'

class CaixasDetalhes(LoginRequiredMixin, TemplateView):
    template_name = 'arq_app/caixa_detalhes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caixa_id = self.kwargs.get('pk')
        context['caixa'] = CaixaDeArquivo.objects.get(pk=caixa_id)
        return context

class CaixaNova(LoginRequiredMixin, CreateView):
    form_class = CaixaDeArquivoForm
    template_name = 'arq_app/caixa_nova.html'
    success_url = '/arq-app/caixas/'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Caixa {form.instance} criada com sucesso.")
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

class Interessados(LoginRequiredMixin, ListView):
    model = Interessado
    template_name = 'arq_app/interessados.html'
    context_object_name = 'interessados'

class InteressadoNovo(LoginRequiredMixin, CreateView):
    form_class = InteressadoForm
    template_name = 'arq_app/interessado_novo.html'
    success_url = '/arq-app/interessados/'

    def form_valid(self, form):

        messages.success(self.request, f"Interessado {form.instance} criado com sucesso.")
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