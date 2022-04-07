from attr import field
from django.contrib import admin
from .models import Categoria,Autor, Editorial, Lectura

#register link
admin.site.site_url = "/lecturas/login"
#nombre de la pagina 
admin.site.site_header = 'Administracion de Lecturas'


# Register your models here.
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['categoria']
    list_display=("categoria","descripcion","created","updated")
admin.site.register(Categoria,CategoriaAdmin)

class AutorAdminAdmin(admin.ModelAdmin):
    search_fields = ['nombre','apellidos','nacionalidad']
    list_display=("nombre","apellidos","nacionalidad","created","updated")
admin.site.register(Autor,AutorAdminAdmin)

class EditorialAdmin(admin.ModelAdmin):
    search_fields = ['editorial']
    list_display=("editorial","created","updated")
admin.site.register(Editorial,EditorialAdmin)

class LecturaAdmin(admin.ModelAdmin):
    search_fields = ['titulo','idioma']
    list_display=("titulo","idioma", "nro_paginas","categoria","editorial","observacion","created")
    
    #readonly_fields=('created','updated')
admin.site.register(Lectura,LecturaAdmin)
