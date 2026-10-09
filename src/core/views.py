from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.db.models import Count, Q
from .models import Libro, Usuario, Admin, Cliente, Ejemplar, Solicitudprestamo, Prestamo, Libro, Editorial, Devolucion, Autor, Escribe
from .reglas import calcular_multa
from django.contrib import messages
from django.conf import settings
import re
from django.db import transaction
import os

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
        libros = Libro.objects.annotate(
            disponibles_count=Count('ejemplar',filter=Q(ejemplar__estado='disponible')))
        correo_usuario = self.request.session.get('correo_usuario')

        if correo_usuario:
            cliente = Cliente.objects.filter(codigo__correo=correo_usuario).first()

            if cliente:
                if cliente.rol.lower() == 'estudiante':
                    libros_solicitados = Solicitudprestamo.objects.filter(codigo_c=cliente,estado='pendiente').values_list('isbn_id', flat=True)
                    libros = libros.annotate(solicitud_pendiente=Q(isbn__in=libros_solicitados))

                    libros_prestados = Prestamo.objects.filter(idsolicitud__codigo_c=cliente,devolucion__isnull=True).values_list('idsolicitud__isbn_id', flat=True)
                    libros = libros.annotate(ya_lo_tiene=Q(isbn__in=libros_prestados))
                else:
                    # Los docentes pueden solicitar el mismo libro varias veces
                    libros = libros.annotate(ya_lo_tiene=Q(pk__in=[]),solicitud_pendiente=Q(pk__in=[]))
            else:
                libros = libros.annotate(ya_lo_tiene=Q(pk__in=[]),solicitud_pendiente=Q(pk__in=[]))
        else:
            libros = libros.annotate(ya_lo_tiene=Q(pk__in=[]),solicitud_pendiente=Q(pk__in=[]))
        return libros







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
    libro = get_object_or_404(Libro, pk=pk)

    if request.session.get('rol') not in ['estudiante', 'docente']:
        if not request.session.get('rol'):
            return redirect('login')
        return redirect('libros')

    if request.method == 'POST':
        correo_usuario = request.session.get('correo_usuario')
        cliente = Cliente.objects.filter(
            codigo__correo=correo_usuario
        ).first()

        if not cliente or cliente.estado.upper() != 'ACTIVO':
            return redirect('libros')

        if cliente.rol.lower() == 'estudiante':
            solicitud_pendiente = Solicitudprestamo.objects.filter(codigo_c=cliente,isbn=libro,estado='pendiente').exists()

            if solicitud_pendiente:
                return redirect('libros')

        if cliente.rol.lower() == 'estudiante':
            ya_lo_tiene = Prestamo.objects.filter(idsolicitud__codigo_c=cliente,idsolicitud__isbn=libro,devolucion__isnull=True).exists()

            if ya_lo_tiene:
                return redirect('libros')

        # Comprobar que el libro tenga al menos un ejemplar disponible
        hay_disponibles = Ejemplar.objects.filter(isbn=libro,estado='disponible').exists()

        if not hay_disponibles:
            return redirect('libros')

        id_sol = f"S-{uuid.uuid4().hex[:7].upper()}"
        Solicitudprestamo.objects.create(idsolicitud=id_sol,codigo_c=cliente,isbn=libro,estado='pendiente')

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
    prestamos = Prestamo.objects.filter(idsolicitud__codigo_c__codigo__correo=correo_usuario, devolucion__isnull=True)

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

    # Solicitudes pendientes: incluyen el contador de ejemplares disponibles
    pendientes = Solicitudprestamo.objects.filter(
        estado='pendiente'
    ).select_related(
        'isbn', 'codigo_c'
    ).annotate(
        disponibles_count=Count(
            'isbn__ejemplar',
            filter=Q(isbn__ejemplar__estado='disponible')
        )
    ).order_by('-idsolicitud')

    # Solicitudes gestionadas: aprobadas o rechazadas, sin calcular disponibilidad
    gestionadas = Solicitudprestamo.objects.filter(
        estado__in=['aprobado', 'rechazado']
    ).select_related(
        'isbn', 'codigo_c'
    ).order_by('-idsolicitud')

    context = {
        'pendientes': pendientes,
        'gestionadas': gestionadas,
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
    autores = Autor.objects.all().order_by('nombre')

    if request.method == 'POST':
        isbn = request.POST.get('isbn', '').strip()
        ideditorial_id = request.POST.get('ideditorial')
        titulo = request.POST.get('titulo', '').strip()
        anio = request.POST.get('anio')
        descripcion = request.POST.get('descripcion')
        autores_seleccionados = request.POST.getlist('autores')
        imagen = request.FILES.get('imagen')
        cantidad_texto = request.POST.get('cantidad_ejemplares', '')
        ubicacion = request.POST.get('ubicacion', '').strip()
        autorrellenar = request.POST.get('autorrellenar_ubicaciones') == 'on'

        def mostrar_error(mensaje):
            return render(request, 'core/form_libro.html', {'editoriales': editoriales,'autores': autores,'accion': 'Registrar','error': mensaje})
        
        try:
            cantidad = int(cantidad_texto)
        except (ValueError, TypeError):
            return mostrar_error('La cantidad de ejemplares debe ser un número entero.')

        if cantidad < 1 or cantidad > 999:
            return mostrar_error('La cantidad debe estar entre 1 y 999.')

        if not re.fullmatch(r'[A-Z][0-9]{2}', ubicacion):
            return mostrar_error('La ubicación debe tener una letra mayúscula y dos números. ''Ejemplo: A03.')

        if autorrellenar and int(ubicacion[1:]) + cantidad - 1 > 99:
            return mostrar_error('Las ubicaciones generadas superarían el formato de dos dígitos. ''Elige otra ubicación inicial o desactiva el autorrellenado.')

        extension = None
        if imagen:
            extension = os.path.splitext(imagen.name)[1].lower()
            if extension not in ['.jpg', '.jpeg', '.png', '.webp']:
                return mostrar_error('Formato no permitido. Usa JPG, JPEG, PNG o WEBP.')

        ubicaciones = []
        if autorrellenar:
            letra = ubicacion[0]
            numero_inicial = int(ubicacion[1:])
            for i in range(cantidad):
                ubicaciones.append(f'{letra}{numero_inicial + i:02d}')

        else:
            ubicaciones = [ubicacion] * cantidad
        with transaction.atomic():
            url_imagen = None

            if imagen:
                nombre_imagen = f'{isbn}{extension}'
                carpeta_imagenes = os.path.join(settings.MEDIA_ROOT, 'Libros')
                os.makedirs(carpeta_imagenes, exist_ok=True)
                ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)

                with open(ruta_imagen, 'wb+') as destino:
                    for fragmento in imagen.chunks():
                        destino.write(fragmento)
                url_imagen = f'/media/Libros/{nombre_imagen}'
            libro = Libro.objects.create(isbn=isbn,ideditorial_id=ideditorial_id,titulo=titulo,anio=anio,descripcion=descripcion,url_imagen=url_imagen)

            for idautor in autores_seleccionados:
                Escribe.objects.create(isbn=libro,idautor_id=idautor)

            codigos_existentes = set(Ejemplar.objects.values_list('codigobarras', flat=True))
            numeros_usados = []

            for codigo in codigos_existentes:
                coincidencia = re.fullmatch(r'EJ(\d+)', codigo, re.IGNORECASE)

                if coincidencia:
                    numeros_usados.append(int(coincidencia.group(1)))
            siguiente_numero = max(numeros_usados, default=0) + 1

            # Crear los ejemplares con códigos únicos
            for ubicacion_ejemplar in ubicaciones:
                while f'EJ{siguiente_numero:03d}' in codigos_existentes:
                    siguiente_numero += 1
                codigo_barras = f'EJ{siguiente_numero:03d}'
                Ejemplar.objects.create(codigobarras=codigo_barras,isbn=libro,ubicacion=ubicacion_ejemplar,estado='disponible')
                codigos_existentes.add(codigo_barras)
                siguiente_numero += 1

        return redirect('libros')

    context = {
        'editoriales': editoriales,
        'autores': autores,
        'accion': 'Registrar'
    }

    return render(request, 'core/form_libro.html', context)



def editar_libro_view(request, pk):
    if request.session.get('rol') != 'admin':
        return redirect('libros')

    libro = get_object_or_404(Libro, pk=pk)
    editoriales = Editorial.objects.all()
    autores = Autor.objects.all().order_by('nombre')

    def mostrar_error(mensaje):
        return render(request, 'core/form_libro.html', {
            'libro': libro,
            'editoriales': editoriales,
            'autores': autores,
            'autores_actuales': list(
                Escribe.objects.filter(isbn=libro).values_list(
                    'idautor_id', flat=True
                )
            ),
            'cantidad_ejemplares': Ejemplar.objects.filter(
                isbn=libro
            ).count(),
            'accion': 'Editar',
            'error': mensaje
        })

    if request.method == 'POST':
        libro.ideditorial_id = request.POST.get('ideditorial')
        libro.titulo = request.POST.get('titulo', '').strip()
        libro.anio = request.POST.get('anio')
        libro.descripcion = request.POST.get('descripcion')
        autores_seleccionados = request.POST.getlist('autores')
        imagen = request.FILES.get('imagen')

        try:
            cantidad_nueva = int(request.POST.get('cantidad_ejemplares', ''))
        except (ValueError, TypeError):
            return mostrar_error('La cantidad de ejemplares debe ser un número entero.')

        if cantidad_nueva < 1 or cantidad_nueva > 999:
            return mostrar_error('La cantidad debe estar entre 1 y 999.')

        ejemplares_actuales = list(Ejemplar.objects.filter(isbn=libro).order_by('codigobarras'))
        cantidad_actual = len(ejemplares_actuales)
        diferencia = cantidad_nueva - cantidad_actual
        ubicaciones_nuevas = []

        if diferencia > 0:
            ubicacion = request.POST.get('ubicacion', '').strip()
            autorrellenar = (request.POST.get('autorrellenar_ubicaciones') == 'on')

            if not re.fullmatch(r'[A-Z][0-9]{2}', ubicacion):
                return mostrar_error('La ubicación debe tener una letra mayúscula y dos ''números. Ejemplo: A03.')

            numero_inicial = int(ubicacion[1:])

            if autorrellenar and numero_inicial + diferencia - 1 > 99:
                return mostrar_error('Las ubicaciones generadas superarían el formato ''de dos dígitos. Elige otra ubicación o desactiva ''el autorrellenado.')

            if autorrellenar:
                letra = ubicacion[0]
                ubicaciones_nuevas = [f'{letra}{numero_inicial + i:02d}'for i in range(diferencia)]
            else:
                ubicaciones_nuevas = [ubicacion] * diferencia
        ejemplares_para_eliminar = []

        if diferencia < 0:
            cantidad_retirar = abs(diferencia)
            ejemplares_elegibles = []

            for ejemplar in ejemplares_actuales:
                tiene_prestamos = Prestamo.objects.filter(codigobarras=ejemplar).exists()

                if (ejemplar.estado.lower() == 'disponible' and not tiene_prestamos):
                    ejemplares_elegibles.append(ejemplar)

            if len(ejemplares_elegibles) < cantidad_retirar:
                return mostrar_error('No se puede reducir la cantidad a 'f'{cantidad_nueva}. Solo hay 'f'{len(ejemplares_elegibles)} ejemplares disponibles ''sin historial de préstamos que puedan retirarse.')

            ejemplares_para_eliminar = ejemplares_elegibles[:cantidad_retirar]
        extension = None

        if imagen:
            extension = os.path.splitext(imagen.name)[1].lower()

            if extension not in ['.jpg', '.jpeg', '.png', '.webp']:
                return mostrar_error('Formato no permitido. Usa JPG, JPEG, PNG o WEBP.')

        with transaction.atomic():
            libro.save()

            Escribe.objects.filter(isbn=libro).delete()

            for idautor in autores_seleccionados:
                Escribe.objects.create(isbn=libro,idautor_id=idautor)

            for ejemplar in ejemplares_para_eliminar:
                ejemplar.delete()

            if diferencia > 0:
                codigos_existentes = set(Ejemplar.objects.values_list('codigobarras', flat=True))
                numeros_usados = []

                for codigo in codigos_existentes:
                    coincidencia = re.fullmatch(r'EJ(\d+)', codigo, re.IGNORECASE)

                    if coincidencia:
                        numeros_usados.append(int(coincidencia.group(1)))

                siguiente_numero = max(numeros_usados, default=0) + 1

                for ubicacion_ejemplar in ubicaciones_nuevas:
                    while f'EJ{siguiente_numero:03d}' in codigos_existentes:
                        siguiente_numero += 1

                    codigo_barras = f'EJ{siguiente_numero:03d}'
                    Ejemplar.objects.create(codigobarras=codigo_barras,isbn=libro,ubicacion=ubicacion_ejemplar,estado='disponible')
                    codigos_existentes.add(codigo_barras)
                    siguiente_numero += 1

        if imagen:
            carpeta_imagenes = os.path.join(settings.MEDIA_ROOT, 'Libros')
            os.makedirs(carpeta_imagenes, exist_ok=True)
            nombre_anterior = None

            if (libro.url_imagen and libro.url_imagen.startswith('/media/Libros/')):
                nombre_anterior = os.path.basename(libro.url_imagen)

            nombre_imagen = f'{libro.isbn}{extension}'
            ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)

            with open(ruta_imagen, 'wb+') as destino:
                for fragmento in imagen.chunks():
                    destino.write(fragmento)

            libro.url_imagen = f'/media/Libros/{nombre_imagen}'
            libro.save(update_fields=['url_imagen'])

            if nombre_anterior and nombre_anterior != nombre_imagen:
                ruta_anterior = os.path.join(carpeta_imagenes, nombre_anterior)
                if os.path.isfile(ruta_anterior):
                    os.remove(ruta_anterior)

        return redirect('libros')

    autores_actuales = list(Escribe.objects.filter(isbn=libro).values_list('idautor_id', flat=True))
    cantidad_ejemplares = Ejemplar.objects.filter(isbn=libro).count()

    context = {
        'libro': libro,
        'editoriales': editoriales,
        'autores': autores,
        'autores_actuales': autores_actuales,
        'cantidad_ejemplares': cantidad_ejemplares,
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
        multa = calcular_multa(prestamo.fechavencimiento, hoy)

        # Buscamos el objeto Admin correspondiente al usuario logueado en la sesión
        correo_admin = request.session.get('correo_usuario')
        admin_obj = Admin.objects.filter(codigo__correo=correo_admin).first()
        
        if not admin_obj:
            # Plan B por si el admin se obtiene de otra forma en la sesión
            admin_obj = Admin.objects.first()

        # Generamos un ID único para la devolución (ej: 'DEV-' + idprestamo)
        id_devolucion = f"DEV{uuid.uuid4().hex[:7].upper()}"

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

        messages.success(request,f'¡Devolución registrada correctamente!\n'f'Cliente: {prestamo.idsolicitud.codigo_c.codigo.nombre}\n'f'ID del préstamo: {prestamo.idprestamo}\n'f'Multa calculada: ${multa:,.0f} COP.')
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