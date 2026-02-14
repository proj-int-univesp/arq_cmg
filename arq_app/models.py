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
                                   verbose_name="Função Mãe")
    codigo = models.CharField(max_length=5, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    class Meta:
        verbose_name = "Subfunção"
        verbose_name_plural = "Subfunções"
    
class AtividadePC(models.Model):
    
    subfuncao_mae = models.ForeignKey(SubFuncaoPC, on_delete=models.PROTECT, 
                                   verbose_name="Subfunção Mãe")
    codigo = models.CharField(max_length=8, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=255, verbose_name="Nome")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    class Meta:
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"

class SerieDocumentalPC(models.Model):
    
    atividade_mae = models.ForeignKey(AtividadePC, on_delete=models.PROTECT, 
                                   verbose_name="Atividade Mãe")
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
    
    def save(self, *args, **kwargs):
        
        if self.numero is None:                        
            self.numero = Numerador.numerar()

        super(CaixaDeArquivo, self).save(*args, **kwargs)

    def __str__(self):
        return f"CXA{self.numero}"
    
    class Meta:
        verbose_name = "Caixa de Arquivo"
        verbose_name_plural = "Caixas de Arquivo"