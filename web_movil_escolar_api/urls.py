from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from django.contrib.auth import views as auth_views
from web_movil_escolar_api.views import bootstrap
from web_movil_escolar_api.views import users
from web_movil_escolar_api.views import auth
from web_movil_escolar_api.views import alumnos
from web_movil_escolar_api.views import maestros
from web_movil_escolar_api.views import materias


urlpatterns = [

    #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view()),

    #Create Alumno
        path('alumno/', alumnos.AlumnoView.as_view()),
    #Alumno Data
        path('lista-alumnos/', alumnos.AlumnoAll.as_view()),
    #Edit Alumno
        #path('alumnos-edit/', users.AlumnosViewEdit.as_view()),    

    #Create Maestro
        path('maestro/', maestros.MaestroView.as_view()),
    #Maestro Data
        path('lista-maestros/', maestros.MaestroAll.as_view()),
    #Edit Maestro
       # path('alumnos-edit/', maestros.MaestrosViewEdit.as_view()),

    #Create Materias
        path('materia/', materias.MateriaView.as_view()),
    #Materias Data
        path('lista-materias/', materias.MateriaAll.as_view()),


    #Total usuario
        path('total-usuarios/', users.TotalUsers.as_view()),

    #Login
        path('login/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
