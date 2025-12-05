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
import json


class MateriaAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        # Verificar que el usuario sea administrador o maestro
        user = request.user
        if not (user.groups.filter(name='Administrador').exists() or 
                user.groups.filter(name='Maestro').exists()):
            return Response({"error": "No autorizado"}, status=403)
        
        materias = Materias.objects.filter(activa=True).order_by("id")
        lista = MateriasSerializer(materias, many=True).data
        for materia in lista:
            if isinstance(materia, dict) and "dias_json" in materia:
                try:
                    materia["dias_json"] = json.loads(materia["dias_json"])
                except Exception:
                    materia["dias_json"] = []
        return Response(lista, 200)


class MateriaView(generics.CreateAPIView):

    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    # Obtener materia por ID
    def get(self, request, *args, **kwargs):
        materia_id = request.GET.get("id")
        
        try:
            materia = Materias.objects.get(id=materia_id, activa=True)
            materia_data = MateriasSerializer(materia, many=False).data
            return Response(materia_data, 200)
        except Materias.DoesNotExist:
            return Response({"error": "Materia no encontrada"}, status=404)

    # Registrar nueva materia
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Verificar que el usuario sea administrador
        user = request.user
        if not user.groups.filter(name='Administrador').exists():
            return Response({"error": "Solo administradores pueden registrar materias"}, status=403)
        
        campos_obligatorios = ['nrc', 
                               'name', 
                               'seccion', 
                               'dias_json', 
                               'hora_i', 
                               'hora_f', 
                               'salon', 
                               'programa', 
                               'profesor_id', 
                               'creditos']
        
        for campo in campos_obligatorios:
            if campo not in request.data or not request.data[campo]:
                return Response({"error": f"El campo {campo} es obligatorio"}, status=400)
        
        nrc = request.data['nrc']
        if Materias.objects.filter(nrc=nrc, activa=True).exists():
            return Response({"error": f"El NRC {nrc} ya está registrado"}, status=400)
        
        if not nrc.isdigit():
            return Response({"error": "El NRC solo puede contener números"}, status=400)
        
        if len(nrc) < 5 or len(nrc) > 6:
            return Response({"error": "El NRC debe tener entre 5 y 6 dígitos"}, status=400)
        
        seccion = str(request.data['seccion'])
        if not seccion.isdigit():
            return Response({"error": "La sección solo puede contener números"}, status=400)
        if len(seccion) > 3:
            return Response({"error": "La sección no puede tener más de 3 dígitos"}, status=400)
        
        dias_json = request.data.get("dias_json", [])
        if not dias_json or len(dias_json) == 0:
            return Response({"error": "Debe seleccionar al menos un día"}, status=400)
        
        hora_i = request.data['hora_i']
        hora_f = request.data['hora_f']
        if hora_i >= hora_f:
            return Response({"error": "La hora de inicio debe ser menor que la hora de finalización"}, status=400)
        
        salon = request.data['salon']
        if len(salon) > 15:
            return Response({"error": "El salón no puede tener más de 15 caracteres"}, status=400)
        
        creditos = str(request.data['creditos'])
        if not creditos.isdigit() or int(creditos) <= 0:
            return Response({"error": "Los créditos deben ser números positivos"}, status=400)
        if len(creditos) > 2:
            return Response({"error": "Los créditos no pueden tener más de 2 dígitos"}, status=400)
        
        profesor_id = request.data['profesor_id']
        try:
            profesor = Maestros.objects.get(id=profesor_id, user__is_active=True)
        except Maestros.DoesNotExist:
            return Response({"error": "El profesor seleccionado no existe"}, status=400)
        
        # Crear la materia
        try:
            materia = Materias.objects.create(nrc=nrc,
                                                name=request.data['name'],
                                                seccion=int(seccion), 
                                                dias_json=json.dumps(request.data['dias_json']),
                                                hora_i=hora_i,
                                                hora_f=hora_f,
                                                salon=salon, 
                                                programa=request.data['programa'],
                                                profesor=profesor,
                                                creditos=int(creditos),
                                                activa=True
            )
            materia.save()
            
            return Response({"Materia creada con ID": materia.id }, 201)
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    # Actualizar datos de la materia
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        
        # Verificar que el usuario sea administrador
        user = request.user
        if not user.groups.filter(name='Administrador').exists():
            return Response({"error": "Solo administradores pueden actualizar materias"}, status=403)
        
        materia = get_object_or_404(Materias, id=request.data["id"], activa=True)
        
        if 'nrc' in request.data:
            nrc = request.data['nrc']
            if Materias.objects.filter(nrc=nrc, activa=True).exclude(id=materia.id).exists():
                return Response({"error": f"El NRC {nrc} ya está registrado"}, status=400)
            if not nrc.isdigit():
                return Response({"error": "El NRC solo puede contener números"}, status=400)
            if len(nrc) < 5 or len(nrc) > 6:
                return Response({"error": "El NRC debe tener entre 5 y 6 dígitos"}, status=400)
            materia.nrc = nrc
        
        if 'seccion' in request.data:
            seccion = str(request.data['seccion'])
            if not seccion.isdigit():
                return Response({"error": "La sección solo puede contener números"}, status=400)
            if len(seccion) > 3:
                return Response({"error": "La sección no puede tener más de 3 dígitos"}, status=400)
            materia.seccion = int(seccion)
        
        if 'dias_json' in request.data:
            dias_json = request.data.get("dias_json", [])
            if not dias_json or len(dias_json) == 0:
                return Response({"error": "Debe seleccionar al menos un día"}, status=400)
            materia.dias_json = json.dumps(dias_json)
        
        if 'hora_i' in request.data and 'hora_f' in request.data:
            if request.data['hora_i'] >= request.data['hora_f']:
                return Response({"error": "La hora de inicio debe ser menor que la hora de finalización"}, status=400)
            materia.hora_i = request.data['hora_i']
            materia.hora_f = request.data['hora_f']
        
        if 'salon' in request.data:
            salon = request.data['salon']
            if len(salon) > 15:
                return Response({"error": "El salón no puede tener más de 15 caracteres"}, status=400)
            materia.salon = salon
        
        if 'creditos' in request.data:
            creditos = str(request.data['creditos'])
            if not creditos.isdigit() or int(creditos) <= 0:
                return Response({"error": "Los créditos deben ser números positivos"}, status=400)
            if len(creditos) > 2:
                return Response({"error": "Los créditos no pueden tener más de 2 dígitos"}, status=400)
            materia.creditos = int(creditos)
        
        if 'profesor_id' in request.data:
            try:
                profesor = Maestros.objects.get(id=request.data['profesor_id'], user__is_active=True)
                materia.profesor = profesor
            except Maestros.DoesNotExist:
                return Response({"error": "El profesor seleccionado no existe"}, status=400)
        
        # Actualizar otros campos
        if 'name' in request.data:
            materia.name = request.data['name']
        if 'programa' in request.data:
            materia.programa = request.data['programa']
        
        materia.save()
        
        return Response({"message": "Materia actualizada correctamente", "materia": MateriasSerializer(materia).data}, 200)
        
   # Eliminar materia (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.groups.filter(name='Administrador').exists():
            return Response({"error": "Solo administradores pueden eliminar materias"}, status=403)
        
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details": "Materia eliminada permanentemente"}, 200)
        except Exception as e:
            return Response({"details": f"Algo pasó al eliminar: {str(e)}"}, 400)

    

# Contar el total de materias por programa educativo
class TotalMaterias(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # Verificar que el usuario sea administrador o maestro
        user = request.user
        if not (user.groups.filter(name='Administrador').exists() or 
                user.groups.filter(name='Maestro').exists()):
            return Response({"error": "No autorizado"}, status=403)
        
        try:
            # TOTAL MATERIAS POR PROGRAMA EDUCATIVO
            icc_count = Materias.objects.filter(
                programa="Ingeniería en Ciencias de la Computación",
                activa=True
            ).count()
            
            lcc_count = Materias.objects.filter(
                programa="Licenciatura en Ciencias de la Computación",
                activa=True
            ).count()
            
            iti_count = Materias.objects.filter(
                programa="Ingeniería en Tecnologías de la Información",
                activa=True
            ).count()
            
            # TOTAL MATERIAS GENERAL
            total_materias = Materias.objects.filter(activa=True).count()
            
            # Respuesta final
            return Response(
                {
                    "icc": icc_count,
                    "lcc": lcc_count,
                    "iti": iti_count,
                    "total": total_materias
                },
                status=200
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)