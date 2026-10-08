from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.db.models import Count, Q
from .models import Libro, Usuario, Admin, Cliente, Ejemplar, Solicitudprestamo, Prestamo, Libro, Editorial, Devolucion
import datetime
from datetime import date
import uuid
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import io, urllib, base64

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
        request.session['correo_usuario'] = usuario.correo
        
        return redirect('inicio')
        
    return render(request, 'core/login.html')

def inicio_view(request):
    return render(request, 'core/principal.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def registro_view(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        identificacion = request.POST.get('identificacion')
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')
        rol = request.POST.get('rol')
        carrera = request.POST.get('carrera', '')

        if Usuario.objects.filter(codigo=codigo).exists() or Usuario.objects.filter(correo=correo).exists():
            return render(request, 'core/registro.html', {
                'error': 'El código institucional o el correo ya están registrados.'
            })

        usuario = Usuario.objects.create(
            codigo=codigo,
            identificacion=identificacion,
            nombre=nombre,
            correo=correo,
            contrasenia=contrasenia
        )

        Cliente.objects.create(
            codigo=usuario,
            rol=rol,
            carrera=carrera,
            estado='activo'
        )

        return redirect('login')

    return render(request, 'core/registro.html')


# Views para visualizacion de prestamos y solicitudes

def solicitar_prestamo_view(request, pk):
    # Obtenemos el libro por su ISBN
    libro = get_object_or_404(Libro, pk=pk)
    
    if request.method == 'POST':
        correo_usuario = request.session.get('correo_usuario')
        cliente = Cliente.objects.filter(codigo__correo=correo_usuario).first()
        
        if cliente:
            id_sol = f"S-{uuid.uuid4().hex[:7].upper()}"
            
            Solicitudprestamo.objects.create(
                idsolicitud=id_sol,
                codigo_c=cliente,
                isbn=libro,
                estado='pendiente'
            )
        return redirect('libros')
    
    context = {
        'libro': libro,
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


# Views para la gestion del administrador

def eliminar_solicitud_view(request, pk):
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitudprestamo, idsolicitud=pk)
        solicitud.delete()
    return redirect('mis_prestamos')

def gestionar_solicitudes_view(request):
    # Verificamos si el usuario logueado es admin
    if request.session.get('rol') != 'admin':
        return redirect('libros')
    
    # Obtenemos todas las solicitudes pendientes (o todas para historial)
    solicitudes = Solicitudprestamo.objects.all().order_by('-idsolicitud')

    context = {
        'solicitudes': solicitudes
    }
    return render(request, 'core/gestionar_solicitudes.html', context)

def cambiar_estado_solicitud_view(request, pk, accion):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    solicitud = get_object_or_404(Solicitudprestamo, idsolicitud=pk)
    
    if accion == 'aprobar':
        ejemplar = Ejemplar.objects.filter(isbn=solicitud.isbn, estado='disponible').first()
        
        if ejemplar:
            solicitud.estado = 'aprobado'
            
            correo_admin = request.session.get('correo_usuario')
            admin_obj = Admin.objects.filter(codigo__correo=correo_admin).first()
            if admin_obj:
                solicitud.codigo_a = admin_obj
            solicitud.save()
            
            id_prestamo = f"P-{uuid.uuid4().hex[:7].upper()}"
            hoy = date.today()
            vencimiento = hoy + datetime.timedelta(days=7) 
            
            Prestamo.objects.create(
                idprestamo=id_prestamo,
                idsolicitud=solicitud,
                codigobarras=ejemplar,
                fechaprestamo=hoy,
                fechavencimiento=vencimiento
            )
            
            ejemplar.estado = 'prestado'
            ejemplar.save()
        else:
            pass
    elif accion == 'rechazar':
        solicitud.estado = 'rechazado'
        
        correo_admin = request.session.get('correo_usuario')
        admin_obj = Admin.objects.filter(codigo__correo=correo_admin).first()
        if admin_obj:
            solicitud.codigo_a = admin_obj
        
        solicitud.save()
    
    return redirect('gestionar_solicitudes')

def registrar_libro_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    editoriales = Editorial.objects.all()

    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        ideditorial_id = request.POST.get('ideditorial')
        titulo = request.POST.get('titulo')
        anio = request.POST.get('anio')
        descripcion = request.POST.get('descripcion')
        url_imagen = request.POST.get('url_imagen')

        # Creamos el registro del libro
        Libro.objects.create(
            isbn=isbn,
            ideditorial_id=ideditorial_id,
            titulo=titulo,
            anio=anio,
            descripcion=descripcion,
            url_imagen=url_imagen
        )
        return redirect('libros')

    context = {
        'editoriales': editoriales,
        'accion': 'Registrar'
    }
    return render(request, 'core/form_libro.html', context)

def editar_libro_view(request, pk):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    libro = get_object_or_404(Libro, pk=pk)
    editoriales = Editorial.objects.all()

    if request.method == 'POST':
        libro.ideditorial_id = request.POST.get('ideditorial')
        libro.titulo = request.POST.get('titulo')
        libro.anio = request.POST.get('anio')
        libro.descripcion = request.POST.get('descripcion')
        libro.url_imagen = request.POST.get('url_imagen')
        libro.save()
        return redirect('libros')

    context = {
        'libro': libro,
        'editoriales': editoriales,
        'accion': 'Editar'
    }
    return render(request, 'core/form_libro.html', context)

def gestionar_permisos_admin_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    # Obtenemos todos los usuarios del sistema
    usuarios = Usuario.objects.all()
    
    # Identificamos qué códigos de usuario ya son administradores
    admins_ids = Admin.objects.values_list('codigo_id', flat=True)

    context = {
        'usuarios': usuarios,
        'admins_ids': admins_ids
    }
    return render(request, 'core/gestionar_permisos.html', context)

def cambiar_permiso_admin_view(request, codigo_usuario):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    usuario = get_object_or_404(Usuario, codigo=codigo_usuario)
    
    # Verificamos si ya es admin
    admin_existente = Admin.objects.filter(codigo=usuario).first()
    
    if admin_existente:
        # Si ya es admin, le quitamos los permisos (borramos de la tabla Admin)
        admin_existente.delete()
    else:
        # Si no es admin, se los otorgamos (creamos el registro en la tabla Admin)
        Admin.objects.create(codigo=usuario)
        
    return redirect('gestionar_permisos_admin')

def procesar_devoluciones_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    # Préstamos que aún no tienen un registro de devolución asociado
    prestamos_activos = Prestamo.objects.filter(devolucion__isnull=True)

    context = {
        'prestamos': prestamos_activos
    }
    return render(request, 'core/procesar_devoluciones.html', context)

def registrar_devolucion_view(request, pk):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    prestamo = get_object_or_404(Prestamo, idprestamo=pk)
    
    if request.method == 'POST':
        observaciones = request.POST.get('observaciones', 'Devolución normal sin novedad')
        
        # Calculamos si hay multa por retraso (ejemplo: valor base por día de atraso o fijo)
        hoy = date.today()
        multa = 0
        if hoy > prestamo.fechavencimiento:
            dias_retraso = (hoy - prestamo.fechavencimiento).days
            multa = dias_retraso * 5000  # Ejemplo: 5000 por cada día de retraso (ajústalo a tu lógica)

        # Buscamos el objeto Admin correspondiente al usuario logueado en la sesión
        correo_admin = request.session.get('correo_usuario')
        admin_obj = Admin.objects.filter(codigo__correo=correo_admin).first()
        
        if not admin_obj:
            # Plan B por si el admin se obtiene de otra forma en la sesión
            admin_obj = Admin.objects.first()

        # Generamos un ID único para la devolución (ej: 'DEV-' + idprestamo)
        id_devolucion = f"DEV-{prestamo.idprestamo}"

        # Creamos el registro en la tabla Devolucion
        Devolucion.objects.create(
            iddevolucion=id_devolucion,
            idprestamo=prestamo,
            codigo=admin_obj,
            fechadevolucion=hoy,
            observaciones=observaciones,
            multa=multa
        )

        # Opcional: Actualizar el estado del ejemplar físico a 'disponible' si tu base de datos lo maneja
        ejemplar = prestamo.codigobarras
        ejemplar.estado = 'disponible'
        ejemplar.save()

        return redirect('procesar_devoluciones')

    return redirect('procesar_devoluciones')

def dashboard_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    # Métricas clave de la base de datos
    total_libros = Libro.objects.count()
    total_prestamos = Prestamo.objects.count()
    total_solicitudes = Solicitudprestamo.objects.count()
    prestamos_activos = Prestamo.objects.filter(devolucion__isnull=True).count()

    context = {
        'total_libros': total_libros,
        'total_prestamos': total_prestamos,
        'total_solicitudes': total_solicitudes,
        'prestamos_activos': prestamos_activos,
    }
    return render(request, 'core/dashboard.html', context)