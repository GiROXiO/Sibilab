from django.shortcuts import render
from django.views.generic import ListView
from .models import Libro, Usuario, Admin, Cliente

class LibroListView(ListView):
    model = Libro
    template_name = 'core/libros.html'
    context_object_name = 'libros'


def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')
        usuario = Usuario.objects.filter(correo=correo).first()

        if usuario is None:
            return render(request, 'core/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

        if usuario.contrasenia != contrasenia:
            return render(request, 'core/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
        if Admin.objects.filter(codigo=usuario.codigo).exists():
            rol = 'admin'
        else:
            cliente = Cliente.objects.filter(codigo=usuario.codigo).first()
            if cliente is not None:
                rol = cliente.rol
            else:
                return render(request, 'core/login.html', {
                    'error': 'Usuario sin rol asignado'
                })
        request.session['rol'] = rol
    return render(request, 'core/login.html')



# Create your views here.