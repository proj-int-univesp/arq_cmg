from django.contrib import admin
from .models import FuncaoPC, SubFuncaoPC, AtividadePC, SerieDocumentalPC

class SubFuncaoPCInline(admin.TabularInline):
    model = SubFuncaoPC
    extra = 2

class FuncaoPCAdmin(admin.ModelAdmin):
    inlines = [SubFuncaoPCInline]
    list_display = ('codigo', 'nome')
    search_fields = ('codigo', 'nome')

class AtividadePCInline(admin.TabularInline):
    model = AtividadePC
    extra = 2

class SubFuncaoPCAdmin(admin.ModelAdmin):
    inlines = [AtividadePCInline]
    list_display = ('codigo', 'nome')
    search_fields = ('codigo', 'nome')

    def has_add_permission(self, request):
        return False

class SerieDocumentalPCInline(admin.StackedInline):
    model = SerieDocumentalPC
    extra = 1

class AtividadePCAdmin(admin.ModelAdmin):
    inlines = [SerieDocumentalPCInline]
    list_display = ('codigo', 'nome')
    search_fields = ('codigo', 'nome')

    def has_add_permission(self, request):
        return False
    
class SerieDocumentalPCAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo_prazo_corrente', 
                    'prazo_corrente', 'prazo_central', 'destinacao')
    search_fields = ('codigo', 'nome', 'tipo_prazo_corrente', 'destinacao')

    def has_add_permission(self, request):
        return False

admin.site.register(FuncaoPC, FuncaoPCAdmin)
admin.site.register(SubFuncaoPC, SubFuncaoPCAdmin)
admin.site.register(AtividadePC, AtividadePCAdmin)
admin.site.register(SerieDocumentalPC, SerieDocumentalPCAdmin)