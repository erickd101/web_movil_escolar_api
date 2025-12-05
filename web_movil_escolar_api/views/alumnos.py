from django.db.models import *
from django.db import transaction
from web_movil_escolar_api.serializers import UserSerializer
from web_movil_escolar_api.serializers import *
from web_movil_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from datetime import datetime
from django.shortcuts import get_object_or_404



class AlumnoAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnosSerializer(alumnos, many=True).data
        user = request.user
        #TODO: Regresar perfil del usuario
        return Response(lista, 200)

class AlumnoView(generics.CreateAPIView):


    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    # Obtener maestro por ID
    def get(self, request, *args, **kwargs):
        alumno_id = request.GET.get("id")
        
        try:
            alumno = Alumnos.objects.get(id=alumno_id, user__is_active=True)
            alumno_data = AlumnosSerializer(alumno, many=False).data
            return Response(alumno_data, 200)
        except Alumnos.DoesNotExist:
            return Response({"error": "Alumno no encontrado"}, status=404)

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        #Serializamos los datos del administrador para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)

        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            #Cifrar la contraseña
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

              # Convertir fecha
            fecha_str = request.data.get("fechaN", None)
            if fecha_str:
               fecha_obj=fecha_str
            else:
                fecha_obj = None

            #Almacenar los datos adicionales del administrador
            alumno = Alumnos.objects.create(user=user,
                                                   clave_alumno= request.data["clave_alumno"],
                                                   telefono= request.data["telefono"],
                                                   curp= request.data["curp"].upper(),
                                                   fechaN= fecha_str,
                                                   rfc= request.data["rfc"].upper(),
                                                   edad= request.data["edad"],
                                                   ocupacion= request.data["ocupacion"])
            alumno.save()
            

            return Response({"Alumno creado con ID": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


# Actualizar datos del alumno
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        # Primero obtenemos el alumno a actualizar
        alumno = get_object_or_404(Alumnos, id=request.data["id"])
        alumno.clave_alumno = request.data["clave_alumno"]
        alumno.telefono = request.data["telefono"]
        alumno.rfc = request.data["rfc"]
        alumno.curp = request.data["curp"]
        alumno.edad = request.data["edad"]
        alumno.ocupacion = request.data["ocupacion"]
        alumno.fechaN = request.data["fechaN"]
        alumno.telefono = request.data["telefono"]
        alumno.save()
        user = alumno.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        return Response({"message": "Alumno actualizado correctamente", "alumno": AlumnosSerializer(alumno).data}, 200)
        
   # Eliminar administrador con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            alumno.user.delete()
            return Response({"details":"Alumno eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
    
    
#Contar el total de cada tipo de usuarios
class TotalUsers(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestrosSerializer(maestros_qs, many=True).data


        total_maestros = maestros_qs.count()

        alumnos_qs = Alumnos.objects.filter(user__is_active=True)
        total_alumnos = alumnos_qs.count()

        return Response(
            {
                "admins": total_admins,
                "maestros": total_maestros,
                "alumnos": total_alumnos
            },
            status=200
        )