from django.urls import path

from django.conf import settings
from django.urls.conf import re_path
from django.views.static import serve

from django.conf.urls.static import static
from . import views
from django.contrib import admin


urlpatterns = [
    #url login http://127.0.0.1:8000/lecturas/login/
    path('' , views.home , name="home"),
    path('login/',views.loginView,name="login"),
    path('registro/',views.view_registro, name='view_registro'),
    path('registro_exitoso/',views.registarUsuario, name='registroUsuario'),
    path('recuperar/',views.view_recuperar_password,name="view_olvido_password"),
    path('recuperar_exitoso/',views.forget_password,name="forget_password"),
    path('change_password/<token>/',views.change_password_view_user ,name='change_password'),
    path('logout/' , views.Logout , name="logout"),
    path('documento/<int:lectura_id>/',views.view_pdf, name='documento_pdf'),
    path('introduccion/', views.view_introdution, name='introdution'),
    path('change-password-user/',views.view_change_password_home,name='change_Password_user'),
    path('edit-user-complete/',views.edit_user_home, name='edit_user_complete'),
    path('edit-password-complete/',views.change_password_user_home, name='edit_passwrod_complete'),
    path('buscar/',views.buscar_lectura,name='buscar'),
    path('audio/',views.cantidad_palabras_x_minuto, name="cantidad_palabras"),
    path('create/',views.comentar,name='create'),
    path('update/<int:id>/',views.view_actualizar_comentario,name='update'),
    path('update/',views.actualizar_comentario,name='update_comentario'),
    path('detele/',views.eliminar_comentario,name='delete'),
    path('eliminar/<int:id>/<int:id_user>',views.eliminar_com, name='eliminar'),
    path('interpretacion/',views.analisis_texto,name="interpretacion"),
    path('instrucciones/',views.view_intrucciones,name="instrucciones"),
    #paso de datos microfono
    path('datos/',views.recolecionDatosMicrofono,name="datos"),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve,{
        'document_root':settings.MEDIA_ROOT,
    })
]

