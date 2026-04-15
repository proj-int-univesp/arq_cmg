from django.test import TestCase
from datetime import datetime, timedelta
from .forms import CaixaDeArquivoForm, DocumentoForm, InteressadoForm, TermoEliminacaoForm
from .models import CaixaDeArquivo, Interessado, SerieDocumentalPC, AtividadePC, SubFuncaoPC, FuncaoPC

# Testa o cadastro de um cidadão
class FormularioCaixaArquivo(TestCase):
    def test_form_valido(self):
        form_data = {
            'descricao': 'Processos 1 a 100/2026',
            'observacoes': 'Este é um teste de cadastro de caixa de arquivo.',
            'cod_localizacao': 'E12'
        }
        form = CaixaDeArquivoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'descricao': '',
            'observacoes': 'Este é um teste de cadastro de caixa de arquivo.',
            'cod_localizacao': 'E12'
        }
        form = CaixaDeArquivoForm(data=form_data)
        self.assertFalse(form.is_valid())

class FormularioDocumento(TestCase):

    def setUp(self):

        self.funcao = FuncaoPC.objects.create(codigo="01", 
                                              nome="Primeira Função")
        self.subfuncao = SubFuncaoPC.objects.create(funcao_mae=self.funcao,
                                              codigo="01.01", 
                                              nome="Primeira Subfunção")
        self.atividade = AtividadePC.objects.create(subfuncao_mae=self.subfuncao,
                                              codigo="01.01.01",
                                              nome="Primeira Atividade")
        self.serie_documental = SerieDocumentalPC.objects.create(atividade_mae=self.atividade,
                                                codigo="01.01.01.01",
                                                nome="Primeira Série Documental",
                                                tipo_prazo_corrente="P",
                                                prazo_corrente=5,
                                                prazo_central=10,
                                                destinacao="P")
        self.interessado = Interessado.objects.create(nome="João Silva",
                                              tipo_doc="F",
                                              numero_doc="12345678900")
        self.caixa = CaixaDeArquivo.objects.create(descricao='Processos 1 a 100/2026',
                                              observacoes='Este é um teste de cadastro de caixa de arquivo.',
                                              cod_localizacao='E12')

    def test_form_valido(self):
        form_data = {
            'serie_documental': self.serie_documental.id,
            'codigo_controle': '1/1999',
            'codigo_protocolo': '15/1999',
            'data_producao': '1999-01-01',
            'interessado': self.interessado.id,
            'assunto': 'Teste de cadastro de documento',
            'data_encerramento': '2000-01-01',
            'quantidade_volumes': 1,
            'caixa': self.caixa.id
        }
        form = DocumentoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'serie_documental': None,
            'codigo_controle': '1/1999',
            'codigo_protocolo': '15/1999',
            'data_producao': '1999-01-01',
            'interessado': self.interessado.id,
            'assunto': 'Teste de cadastro de documento',
            'data_encerramento': '2000-01-01',
            'quantidade_volumes': 1,
            'caixa': self.caixa.id
        }
        form = DocumentoForm(data=form_data)
        self.assertFalse(form.is_valid())

class FormularioInteressado(TestCase):
    def test_form_valido(self):
        form_data = {
            'nome': 'João Silva',
            'tipo_doc': 'F',
            'numero_doc': '32557580848'
        }
        form = InteressadoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'nome': 'João Silva',
            'tipo_doc': 'F',
            'numero_doc': '00000000000'
        }
        form = InteressadoForm(data=form_data)
        self.assertFalse(form.is_valid())

class FormularioTermoEliminacao(TestCase):
    def test_form_valido(self):
        form_data = {
            'numeroTermo': '1/2026',
            'dataTermo': '2026-01-01',
            'numeroEdital': '31/2025',
            'observacoes': ''
        }
        form = TermoEliminacaoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        form_data = {
            'numeroTermo': '',
            'dataTermo': '2026-01-01',
            'numeroEdital': '31/2025',
            'observacoes': ''
        }
        form = TermoEliminacaoForm(data=form_data)
        self.assertFalse(form.is_valid())