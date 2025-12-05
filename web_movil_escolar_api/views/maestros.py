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
from django.shortcuts import get_object_or_404
from datetime import datetime


class MaestroAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestrosSerializer(maestros, many=True).data
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except Exception:
                    maestro["materias_json"] = []
        user = request.user
        return Response(lista, 200)

class MaestroView(generics.CreateAPIView):


    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    # Obtener maestro por ID
    def get(self, request, *args, **kwargs):
        maestro_id = request.GET.get("id")
        
        try:
            maestro = Maestros.objects.get(id=maestro_id, user__is_active=True)
            maestro_data = MaestrosSerializer(maestro, many=False).data
            return Response(maestro_data, 200)
        except Maestros.DoesNotExist:
            return Response({"error": "Maestro no encontrado"}, status=404)


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
            #Valida si existe el usuario o el email registrado
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

            maestro = Maestros.objects.create(user=user,
                                                   clave_maestro= request.data["clave_maestro"],
                                                   telefono= request.data["telefono"],
                                                   fechaN= fecha_str,
                                                   rfc= request.data["rfc"].upper(),
                                                   cubiculo = request.data["cubiculo"],
                                                   area = request.data["area"],
                                                   materias_json = json.dumps(request.data["materias_json"]))
            maestro.save()
            

            return Response({"Maestro creado con ID": maestro.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

# Actualizar datos del maestro
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        # Primero obtenemos el maestro a actualizar
        maestro = get_object_or_404(Maestros, id=request.data["id"])
        maestro.clave_maestro = request.data["clave_maestro"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"]
        maestro.fechaN = request.data["fechaN"]
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area = request.data["area"]
        maestro.materias_json = json.dumps(request.data["materias_json"])
        maestro.save()
        # Actualizamos los datos
        user = maestro.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()
        
        return Response({"message": "Maestro actualizado correctamente", "maestro": MaestrosSerializer(maestro).data}, 200)
        
    # Eliminar administrador con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        try:
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
    

class TotalUsers(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # Total administradores
        admin_qs = Administradores.objects.filter(user__is_active=True)
        total_admins = admin_qs.count()

        # Totall maestros
        maestros_qs = Maestros.objects.filter(user__is_active=True)
        lista_maestros = MaestrosSerializer(maestros_qs, many=True).data

        for maestro in lista_maestros:
            try:
                maestro["materias_json"] = json.loads(maestro["materias_json"])
            except Exception:
                maestro["materias_json"] = []

        total_maestros = maestros_qs.count()

        #  Total alumnos
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