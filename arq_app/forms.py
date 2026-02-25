from django import forms
from .models import CaixaDeArquivo, Documento, Interessado, SerieDocumentalPC
import requests

class CaixaDeArquivoForm(forms.ModelForm):

    class Meta:
        model = CaixaDeArquivo
        fields = ('descricao', 'observacoes', 'cod_localizacao')

class DocumentoForm(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ('serie_documental', 'codigo_controle', 'codigo_protocolo', 
                  'data_producao', 'interessado', 'assunto', 'data_encerramento',
                  'quantidade_volumes', 'caixa')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['serie_documental'].queryset = SerieDocumentalPC.objects.order_by('codigo')     
        self.fields['interessado'].queryset = Interessado.objects.order_by('nome')     
        self.fields['caixa'].queryset = CaixaDeArquivo.objects.order_by('numero')

class InteressadoForm(forms.ModelForm):

    class Meta:
        model = Interessado
        fields = ('nome', 'tipo_doc', 'numero_doc')
                     
    def clean_numero_doc(self):
        
        numero_doc = self.cleaned_data.get('numero_doc')
        tipo_doc = self.cleaned_data.get('tipo_doc')

        if tipo_doc != 'N':
        
            if not numero_doc:
                raise forms.ValidationError('Este campo é obrigatório ao escolher o tipo de documento CPF ou CNPJ.')
            
            if not numero_doc.isdigit():
                raise forms.ValidationError('Número do documento inválido. Deve conter apenas dígitos.')

            if tipo_doc == 'F' and len(numero_doc) != 11:
                raise forms.ValidationError('Número do CPF deve conter 11 dígitos.')
            elif tipo_doc == 'J' and len(numero_doc) != 14:
                raise forms.ValidationError('Número do CNPJ deve conter 14 dígitos.')

            try:
                if tipo_doc == 'F':
                    response = requests.get(f'https://api.invertexto.com/v1/validator?token=24484|JzFFc5C7q2IK3EnAF6FJWtIkKU7cxLzV&value={numero_doc}&type=cpf')
                else:
                    response = requests.get(f'https://api.invertexto.com/v1/validator?token=24484|JzFFc5C7q2IK3EnAF6FJWtIkKU7cxLzV&value={numero_doc}&type=cnpj')
                
                data = response.json()

                if not data['valid']:
                    raise forms.ValidationError('Número de documento inválido. Verifique se foi digitado corretamente.')
            
            except requests.exceptions.RequestException:
                raise forms.ValidationError('Não foi possível validar o número do documento. Verifique sua conexão com a internet.')
        else:
            numero_doc = None  

        return numero_doc 