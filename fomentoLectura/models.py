from django.db import models
from django.contrib.auth.models import  User

# Create your models here.


class Autor(models.Model):
    nombre=models.CharField('Nombre',max_length=50, blank=False, null=False)
    apellidos=models.CharField(max_length=50,blank=False, null=False)
    nacionalidad=models.CharField(max_length=50,blank=True, null=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)
    def __str__(self) :
        return self.nombre+" "+self.apellidos
    
class Categoria(models.Model):
    categoria=models.CharField(max_length=50)
    descripcion=models.TextField(max_length=500)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)
    def __str__(self) :
        return self.categoria

    
class Editorial(models.Model):
    editorial=models.CharField(max_length=50)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)
    def __str__(self) :
        return self.editorial


IDIOMA_CHOICES=(
    ("Español", "Español"),
    ("Ingles", "Ingles"),  
    
)
 
class Lectura(models.Model):
    isbn=models.CharField(max_length=20,null=True,blank=True)
    titulo=models.CharField(max_length=60)
    idioma=models.CharField(max_length=60,choices=IDIOMA_CHOICES,default='Español')
    nro_paginas=models.PositiveIntegerField()
    autores= models.ManyToManyField(Autor,null=False,blank=False)
    categoria=models.ForeignKey(Categoria, on_delete=models.PROTECT)
    editorial=models.ForeignKey(Editorial, on_delete=models.PROTECT,null=True)
    portada=models.ImageField(upload_to='lectura',null=False)
    documento=models.FileField(upload_to='archivos',null=False)
    descripcion=models.TextField(max_length=500,null=True)
    observacion=models.TextField(max_length=500,null=True,blank=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)
    def __str__(self) :
        return self.titulo 


class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Comentario(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    lectura=models.ForeignKey(Lectura, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=500)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comentario


