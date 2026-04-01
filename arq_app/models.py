from django.core.exceptions import ValidationError
from django.db import models, transaction

class Numerador(models.Model):
    
    ultimo_num = models.PositiveBigIntegerField("último número", default=0)

    @classmethod
    def numerar(cls):
        
        with transaction.atomic():
            
            try:
                numeracao = cls.objects.select_for_update().get()
            except cls.DoesNotExist:          
                numeracao = cls.objects.create()
            
            numeracao.ultimo_num += 1
            numeracao.save()
            return numeracao.ultimo_num

class FuncaoPC(models.Model):
    
    codigo = models.CharField(max_length=2, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    class Meta:
        verbose_name = "Função"
        verbose_name_plural = "Funções"

class SubFuncaoPC(models.Model):
    
    funcao_mae = models.ForeignKey(FuncaoPC, on_delete=models.PROTECT, 
                                   related_name="subfuncoes", verbose_name="Função Mãe")
    codigo = models.CharField(max_length=5, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    class Meta:
        verbose_name = "Subfunção"
        verbose_name_plural = "Subfunções"
    
class AtividadePC(models.Model):
    
    subfuncao_mae = models.ForeignKey(SubFuncaoPC, on_delete=models.PROTECT, 
                                   related_name="atividades", verbose_name="Subfunção Mãe")
    codigo = models.CharField(max_length=8, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    class Meta:
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"

class SerieDocumentalPC(models.Model):
    
    atividade_mae = models.ForeignKey(AtividadePC, on_delete=models.PROTECT, 
                                   related_name="series_documentais", verbose_name="Atividade Mãe")
    codigo = models.CharField(max_length=11, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome")
    tipo_prazo_corrente = models.CharField(max_length=1, choices=[
        ("C", "Até a aprovação das contas"),
        ("P", "Período determinado"),
        ("V", "Vigência")
    ], default="V", verbose_name="Tipo de Prazo Corrente")
    prazo_corrente = models.PositiveIntegerField(verbose_name="Prazo na Fase Corrente (anos)")
    prazo_central = models.PositiveIntegerField(verbose_name="Prazo no Arquivo Central (anos)")
    destinacao = models.CharField(max_length=1, choices=[
        ("E", "Eliminar"),
        ("P", "Preservar")
    ], default="P", verbose_name="Destinação")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    legislacao_norma = models.TextField(blank=True, verbose_name="Legislação/Norma")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    class Meta:
        verbose_name = "Série Documental"
        verbose_name_plural = "Séries Documentais"

class Interessado(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome")
    tipo_doc = models.CharField(max_length=1, choices=[
        ("F", "CPF"),
        ("J", "CNPJ"),
        ("N", "Não Possui")
    ], default="N", verbose_name="Tipo de Documento")
    numero_doc = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número do Documento")

    def __str__(self):
        return f'{self.nome} ({self.numero_doc if self.numero_doc else ""})'
        
    class Meta:
        verbose_name = "Interessado"
        verbose_name_plural = "Interessados"

class CaixaDeArquivo(models.Model):
    numero = models.PositiveIntegerField(verbose_name="Número da Caixa", unique=True)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    cod_localizacao = models.CharField(max_length=20, verbose_name="Código de Localização", blank=True, null=True)
    termoEliminacao = models.ForeignKey('TermoEliminacaoDocumentos', on_delete=models.SET_NULL, blank=True, null=True,
                                        related_name="caixas_eliminadas", verbose_name="Termo de Eliminação")

    def save(self, *args, **kwargs):
        
        if self.numero is None:                        
            self.numero = Numerador.numerar()

        super(CaixaDeArquivo, self).save(*args, **kwargs)

    def __str__(self):
        return f"CXA{self.numero}"
    
    class Meta:
        verbose_name = "Caixa de Arquivo"
        verbose_name_plural = "Caixas de Arquivo"

class Documento(models.Model):
    serie_documental = models.ForeignKey(SerieDocumentalPC, on_delete=models.PROTECT, 
                                related_name="documentos", verbose_name="Série Documental")
    codigo_controle = models.CharField(max_length=30, blank=True, 
                                verbose_name="Código de Controle")
    codigo_protocolo = models.CharField(max_length=30, blank=True, 
                                verbose_name="Código de Protocolo")
    data_producao = models.DateField(verbose_name="Data de Produção")
    interessado = models.ForeignKey(Interessado, on_delete=models.PROTECT, 
                                related_name="documentos", verbose_name="Interessado")
    assunto = models.CharField(max_length=255, 
                                verbose_name="Assunto")
    data_encerramento = models.DateField(blank=True, null=True, 
                                verbose_name="Data de Encerramento")
    quantidade_volumes = models.PositiveIntegerField(default=1, 
                                verbose_name="Quantidade de Volumes")
    caixa = models.ForeignKey(CaixaDeArquivo, on_delete=models.PROTECT, blank=True, null=True, 
                                related_name="documentos", verbose_name="Caixa de Arquivo")

    def clean(self):
        super().clean()
        # Validação: documento não pode ser colocado em uma caixa com documentos de outro tipo documental
        if self.caixa:
            caixa_documentos = self.caixa.documentos.exclude(id=self.id)
            if caixa_documentos.exists():
                caixa_serie = caixa_documentos.first().serie_documental
                if caixa_serie != self.serie_documental:
                    raise ValidationError("O documento não pode ser colocado nesta caixa, pois ela contém documentos de outra série documental.")
    
    def __str__(self):
        return f"DOC{self.id}"
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

class TermoEliminacaoDocumentos(models.Model):
    numeroTermo = models.CharField(max_length=20, unique=True, verbose_name="Número do Termo")
    dataTermo = models.DateField(verbose_name="Data do Termo")
    numeroEdital = models.CharField(max_length=20, unique=True, verbose_name="Número do Edital")
    observacoes = models.TextField(blank=True, verbose_name="Observações")

    def __str__(self):
        return f"{self.numeroTermo} ({self.dataTermo.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Termo de Eliminação de Documentos"
        verbose_name_plural = "Termos de Eliminação de Documentos"