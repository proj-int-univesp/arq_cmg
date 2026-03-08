from rest_framework import serializers
from .models import SerieDocumentalPC, CaixaDeArquivo

class SerieDocumentalPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerieDocumentalPC
        fields = '__all__'

class CaixaDeArquivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaixaDeArquivo
        fields = ('numero', 'descricao')
