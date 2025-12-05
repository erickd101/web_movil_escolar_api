from django.db.models import *
from web_movil_escolar_api.serializers import *
from web_movil_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})

        if not serializer.is_valid():
            return Response({"error": "Credenciales inválidas"}, status= status.HTTP_401_UNAUTHORIZED)
        
        user = serializer.validated_data['user']
        if user.is_active:

            roles = user.groups.all()
            role_names = []
            for role in roles:
                role_names.append(role.name)
            role_names = role_names[0]

            token, created = Token.objects.get_or_create(user=user)
            
            if role_names == 'Alumno':
                alumno = Alumnos.objects.filter(user=user).first()
                alumno = AlumnosSerializer(alumno).data
                alumno["token"] = token.key
                alumno["rol"] = "Alumno"
                return Response(alumno,200)
            if role_names == 'Maestro':
                maestro = Maestros.objects.filter(user=user).first()
                maestro = MaestrosSerializer(maestro).data
                maestro["token"] = token.key
                maestro["rol"] = "Maestro"
                return Response(maestro,200)
            if role_names == 'Administrador':
                user = UserSerializer(user, many=False).data
                user['token'] = token.key
                user["rol"] = "Administrador"
                return Response(user,200)
            else:
                return Response({"details":"Forbidden"},403)
                pass
            
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        print("logout")
        user = request.user
        print(str(user))
        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()

            return Response({'logout': True})

        return Response({'logout': False})