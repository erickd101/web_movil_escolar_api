from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
import json  # 👈 Asegúrate de importar json


from django.db import models
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"
 
class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del admin "+self.user.first_name+" "+self.user.last_name

#TODO: Agregar perfiles para estudiantes y profesores
class Alumnos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_alumno = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    curp = models.CharField(max_length=18, unique=True, null=False, blank=False)
    fechaN = models.DateField(null=False, blank=False)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del alumno "+self.user.first_name+" "+self.user.last_name
    
class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_maestro = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    fechaN = models.DateField(null=False, blank=False)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    cubiculo = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    materias_json = models.TextField(default='[]', blank=True, null=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)


class Materias(models.Model):
    id = models.BigAutoField(primary_key=True)
    nrc = models.CharField(max_length=6, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    seccion = models.CharField(max_length=3, null=False, blank=False)
    dias_json = models.TextField(default='[]', blank=True, null=True)
    hora_i = models.TimeField(null=False, blank=False)
    hora_f = models.TimeField(null=False, blank=False)
    salon = models.CharField(max_length=15, null=False, blank=False)
    programa = models.CharField(max_length=100, null=False, blank=False)
    profesor = models.ForeignKey(Maestros, on_delete=models.CASCADE, null=False, blank=False, default=None)
    creditos = models.IntegerField(null=False, blank=False)
    activa = models.BooleanField(default=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nrc} - {self.nombre} (Sección {self.seccion})"

    def get_dias_list(self):
        """Convierte el JSON string de vuelta a lista Python"""
        try:
            return json.loads(self.dias_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_dias_list(self, dias_list):
        """Convierte una lista Python a JSON string"""
        self.dias_json = json.dumps(dias_list)


    def __str__(self):
        return "Perfil del maestro "+self.user.first_name+" "+self.user.last_name
    



    def get_materias_list(self):
        """Convierte el JSON string de vuelta a lista Python"""
        try:
            return json.loads(self.materias_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_materias_list(self, materias_list):
        """Convierte una lista Python a JSON string"""
        self.materias_json = json.dumps(materias_list)