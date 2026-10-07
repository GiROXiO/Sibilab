"""
URL configuration for sibilab_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('principal/', views.inicio_view, name='inicio'),
    path('admin/', admin.site.urls),
    path('libros/', views.LibroListView.as_view(), name='libros'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('prestamo/solicitar/<str:pk>/', views.solicitar_prestamo_view, name='solicitar_prestamo'),
    path('mis-prestamos/', views.mis_prestamos_view, name='mis_prestamos'),
    path('solicitud/eliminar/<str:pk>/', views.eliminar_solicitud_view, name='eliminar_solicitud'),
    path('panel-admin/solicitudes/', views.gestionar_solicitudes_view, name='gestionar_solicitudes'),
    path('panel-admin/solicitudes/<str:pk>/<str:accion>/', views.cambiar_estado_solicitud_view, name='cambiar_estado_solicitud'),
    path('panel-admin/libro/nuevo/', views.registrar_libro_view, name='registrar_libro'),
    path('panel-admin/libro/editar/<str:pk>/', views.editar_libro_view, name='editar_libro'),
    path('panel-admin/permisos/', views.gestionar_permisos_admin_view, name='gestionar_permisos_admin'),
    path('panel-admin/permisos/cambiar/<str:codigo_usuario>/', views.cambiar_permiso_admin_view, name='cambiar_permiso_admin'),
    path('panel-admin/devoluciones/', views.procesar_devoluciones_view, name='procesar_devoluciones'),
    path('panel-admin/devoluciones/registrar/<str:pk>/', views.registrar_devolucion_view, name='registrar_devolucion'),
]