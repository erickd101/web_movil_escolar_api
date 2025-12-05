from django.db.models import *
from web_movil_escolar_api.serializers import *
from web_movil_escolar_api.models import *
from rest_framework import permissions, generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):

    permission_classes = [permissions.AllowAny]   
    authentication_classes = []                  

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data['user']

        if not user.is_active:
            return Response({"details": "Usuario inactivo"}, status=403)

        roles = user.groups.all()
        if not roles:
            return Response({"details": "Usuario sin rol"}, status=403)

        role_name = roles[0].name   # Primer grupo

        token, created = Token.objects.get_or_create(user=user)

        if role_name == 'Alumno':
            alumno = Alumnos.objects.filter(user=user).first()
            data = AlumnosSerializer(alumno).data
            data["token"] = token.key
            data["rol"] = "Alumno"
            return Response(data, 200)

        if role_name == 'Maestro':
            maestro = Maestros.objects.filter(user=user).first()
            data = MaestrosSerializer(maestro).data
            data["token"] = token.key
            data["rol"] = "Maestro"
            return Response(data, 200)

        if role_name == 'Administrador':
            data = UserSerializer(user, many=False).data
            data["token"] = token.key
            data["rol"] = "Administrador"
            return Response(data, 200)

        return Response({"details": "Rol no reconocido"}, status=403)


# ✅ LOGOUT PROTEGIDO CORRECTAMENTE
class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        user = request.user

        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()
            return Response({'logout': True})

        return Response({'logout': False})
