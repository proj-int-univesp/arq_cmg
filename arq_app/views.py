import weasyprint
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Min, Q, F
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView

from .forms import CaixaDeArquivoForm, DocumentoForm, InteressadoForm, TermoEliminacaoForm
from .models import CaixaDeArquivo, Documento, FuncaoPC, Interessado, SerieDocumentalPC, TermoEliminacaoDocumentos


@login_required
def relatorio_eliminacao_pdf(request):
    hoje = timezone.now().date()
    # Buscar tipos documentais candidatos à eliminação
    series = SerieDocumentalPC.objects.filter(destinacao='E').order_by('codigo')
    tipos_documentais = []
    for serie in series:
        data_limite = hoje.replace(year=hoje.year - serie.prazo_central)
        caixas = CaixaDeArquivo.objects.filter(
            termoEliminacao=None,
            documentos__serie_documental=serie,
            documentos__data_producao__lte=data_limite
        ).distinct().order_by('numero')
        if caixas.exists():
            caixas_info = []
            for caixa in caixas:
                docs = caixa.documentos.filter(serie_documental=serie)
                if docs.exists():
                    data_inicial = docs.order_by('data_producao').first().data_producao
                    data_final = docs.order_by('data_producao').last().data_producao
                else:
                    data_inicial = data_final = None
                caixas_info.append({
                    'numero': caixa.numero,
                    'descricao': caixa.descricao,
                    'data_inicial': data_inicial,
                    'data_final': data_final,
                })
            tipos_documentais.append({
                'codigo': serie.codigo,
                'nome': serie.nome,
                'prazo_central': serie.prazo_central,
                'caixas': caixas_info
            })

    html = render_to_string('arq_app/relatorio_eliminacao_pdf.html', {'tipos_documentais': tipos_documentais})
    pdf = weasyprint.HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_eliminacao.pdf"'
    return response

@login_required
@require_POST
def associar_termo_caixa(request):
    caixa_id = request.POST.get('caixa_id')
    termo_id = request.POST.get('termo_id')
    if caixa_id and termo_id:
        caixa = get_object_or_404(CaixaDeArquivo, pk=caixa_id)
        termo = get_object_or_404(TermoEliminacaoDocumentos, pk=termo_id)
        caixa.termoEliminacao = termo
        caixa.save()
        messages.success(request, f'Caixa de arquivo {caixa} incluída no Termo de Eliminação nº {termo}.')
    else:
        messages.error(request, 'Selecione um termo para associar.')

    return redirect(request.META.get('HTTP_REFERER', '/'))

class MenuView(LoginRequiredMixin, TemplateView):
    template_name = 'arq_app/menu.html'

class CaixasAptasEliminacaoListView(LoginRequiredMixin, ListView):
    model = CaixaDeArquivo
    template_name = 'arq_app/regua_eliminacao_detalhes.html'
    context_object_name = 'caixas_aptas'


    def get_queryset(self):
        serie_codigo = self.kwargs.get('serie_codigo')
        hoje = timezone.now().date()
        try:
            serie = SerieDocumentalPC.objects.get(codigo=serie_codigo)
        except SerieDocumentalPC.DoesNotExist:
            return CaixaDeArquivo.objects.none()
        data_limite = hoje.replace(year=hoje.year - serie.prazo_central)
        return CaixaDeArquivo.objects.filter(
            termoEliminacao=None,
            documentos__serie_documental=serie,
            documentos__data_producao__lte=data_limite
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['termos_eliminacao'] = TermoEliminacaoDocumentos.objects.all()
        return context

class CaixasdeArquivo(LoginRequiredMixin, ListView):
    model = CaixaDeArquivo
    template_name = 'arq_app/caixas.html'
    context_object_name = 'caixas'

    def get_queryset(self):
        return CaixaDeArquivo.objects.filter(termoEliminacao=None).order_by('-numero')

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

class CaixasEliminadas(LoginRequiredMixin, ListView):
    model = CaixaDeArquivo
    template_name = 'arq_app/caixas_eliminadas.html'
    context_object_name = 'caixas'

    def get_queryset(self):
        return CaixaDeArquivo.objects.filter(termoEliminacao__isnull=False).order_by('-numero')
    
class Documentos(LoginRequiredMixin, ListView):
    model = Documento
    template_name = 'arq_app/documentos.html'
    context_object_name = 'documentos'

    def get_queryset(self):
        return Documento.objects.filter(caixa__termoEliminacao=None).order_by('-id')

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

class DocumentosEliminados(LoginRequiredMixin, ListView):
    model = Documento
    template_name = 'arq_app/documentos_eliminados.html'
    context_object_name = 'documentos'

    def get_queryset(self):
        return Documento.objects.filter(caixa__termoEliminacao__isnull=False).order_by('-id')   

class Interessados(LoginRequiredMixin, ListView):
    model = Interessado
    template_name = 'arq_app/interessados.html'
    context_object_name = 'interessados'
    ordering = ['nome']

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

class PlanoClassificacaoListView(LoginRequiredMixin, ListView):
    model = FuncaoPC
    template_name = 'arq_app/plano_classificacao.html'
    context_object_name = 'funcoes'
    ordering = ['codigo']

class SeriesDocumentaisEliminarListView(LoginRequiredMixin, ListView):
    model = SerieDocumentalPC
    template_name = 'arq_app/regua_eliminacao.html'
    context_object_name = 'series_eliminar'

    def get_queryset(self):
        hoje = timezone.now().date()
        queryset = SerieDocumentalPC.objects.filter(destinacao='E')\
            .annotate(
                min_data_producao=Min('documentos__data_producao'),
                caixas_count=Count('documentos__caixa', distinct=True),
                limite_data=F('prazo_central')
            )
        resultado = []
        for serie in queryset:
            if serie.min_data_producao:
                data_limite = hoje.replace(year=hoje.year - serie.prazo_central)
                caixas_relacionadas = CaixaDeArquivo.objects.filter(
                    termoEliminacao=None,
                    documentos__serie_documental=serie,
                    documentos__data_producao__lte=data_limite
                ).distinct().count()
                if caixas_relacionadas > 0:
                    serie.caixas_relacionadas = caixas_relacionadas
                    resultado.append(serie)
        resultado.sort(key=lambda s: s.caixas_relacionadas, reverse=True)
        return resultado

class TabelaTemporalidadeListView(LoginRequiredMixin, ListView):
    model = FuncaoPC
    template_name = 'arq_app/tabela_temporalidade.html'
    context_object_name = 'funcoes'
    ordering = ['codigo']

class TermoEliminacaoDetalhes(LoginRequiredMixin, TemplateView):
    
    template_name = 'arq_app/termo_detalhes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        termo_id = self.kwargs.get('pk')
        context['termo'] = TermoEliminacaoDocumentos.objects.get(pk=termo_id)
        
        return context
    
class TermoEliminacaoEditar(LoginRequiredMixin, UpdateView):
    model = TermoEliminacaoDocumentos
    form_class = TermoEliminacaoForm
    template_name = 'arq_app/termo_editar.html'
    success_url = '/arq-app/termos/'

    def form_valid(self, form):

        messages.success(self.request, f"Termo de Eliminação nº {self.object} editado com sucesso.")
        return super(TermoEliminacaoEditar,self).form_valid(form)

class TermoEliminacaoExcluir(LoginRequiredMixin, DeleteView):
    context_object_name = 'termo'
    model = TermoEliminacaoDocumentos
    template_name = 'arq_app/termo_excluir.html'
    success_url = '/arq-app/termos/'
    
    def form_valid(self, form):

        messages.success(self.request, f"Termo de Eliminação nº {self.object} excluído com sucesso.")
        return super(TermoEliminacaoExcluir,self).form_valid(form)

class TermoEliminacaoNovo(LoginRequiredMixin, CreateView):
    form_class = TermoEliminacaoForm
    template_name = 'arq_app/termo_novo.html'
    success_url = '/arq-app/termos/'

    def form_valid(self, form):

        messages.success(self.request, f"Termo de Eliminação nº {form.instance} cadastrado com sucesso.")
        return super(TermoEliminacaoNovo,self).form_valid(form)

class TermosEliminacao(LoginRequiredMixin, ListView):
    model = TermoEliminacaoDocumentos
    template_name = 'arq_app/termos.html'
    context_object_name = 'termos'
    ordering = ['-dataTermo']