from rest_framework import generics
from .models import SerieDocumentalPC, CaixaDeArquivo
from .serializers import SerieDocumentalPCSerializer, CaixaDeArquivoSerializer

class SerieDocumentalPCListAPIView(generics.ListAPIView):
    queryset = SerieDocumentalPC.objects.all()
    serializer_class = SerieDocumentalPCSerializer

class CaixasPorSerieDocumentalAPIView(generics.ListAPIView):
    serializer_class = CaixaDeArquivoSerializer

    def get_queryset(self):
        codigo = self.kwargs.get('codigo')
        return CaixaDeArquivo.objects.filter(documentos__serie_documental__codigo=codigo).distinct()
