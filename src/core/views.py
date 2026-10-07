from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.db.models import Count, Q
from .models import Libro, Usuario, Admin, Cliente, Ejemplar, Solicitudprestamo, Prestamo

class LibroListView(ListView):
    model = Libro
    template_name = 'core/libros.html'
    context_object_name = 'libros'

    def get_queryset(self):
        # Aquí es donde Django debe calcular el conteo de ejemplares disponibles por libro
        return Libro.objects.annotate(
            disponibles_count=Count('ejemplar', filter=Q(ejemplar__estado='disponible'))
        )

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

def inicio_view(request):
    return render(request, 'core/principal.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def solicitar_prestamo_view(request, pk):
    # Obtenemos el libro por su ISBN
    libro = get_object_or_404(Libro, pk=pk)
    
    # Filtramos únicamente los ejemplares físicos de este libro que estén disponibles
    ejemplares_disponibles = Ejemplar.objects.filter(isbn=libro, estado='disponible')

    if request.method == 'POST':
        codigo_barras = request.POST.get('ejemplar')
        # Aquí irá el código para guardar la SolicitudPrestamo en el siguiente feature
        return redirect('libros')

    context = {
        'libro': libro,
        'ejemplares': ejemplares_disponibles
    }
    return render(request, 'core/solicitar_prestamo.html', context)

def mis_prestamos_view(request):
    if not request.session.get('rol'):
        return redirect('login')
    
    # Obtenemos las solicitudes y préstamos del cliente logueado
    # (Ajusta el filtro de sesión según cómo guardes el identificador del usuario)
    correo_usuario = request.session.get('correo_usuario')
    
    solicitudes = Solicitudprestamo.objects.filter(codigo_c__codigo__correo=correo_usuario)
    prestamos = Prestamo.objects.filter(idsolicitud__codigo_c__codigo__correo=correo_usuario)

    context = {
        'solicitudes': solicitudes,
        'prestamos': prestamos
    }
    return render(request, 'core/mis_prestamos.html', context)

def eliminar_solicitud_view(request, pk):
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitudprestamo, idsolicitud=pk)
        solicitud.delete()
    return redirect('mis_prestamos')