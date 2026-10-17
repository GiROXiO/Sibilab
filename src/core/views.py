from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.db.models import Count, Q
from .models import Libro, Usuario, Admin, Cliente, Ejemplar, Solicitudprestamo, Prestamo, Libro, Editorial, Devolucion, Autor, Escribe
from .reglas import calcular_multa
from django.contrib import messages
from django.conf import settings
import re
from django.db import transaction
from django.db import IntegrityError
import os

import operator
from functools import reduce
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

    def _aplicar_filtro_busqueda(self, queryset, q):
        if not q:
            return queryset

        palabras = q.split()
        filtros_palabras = []

        for palabra in palabras:
            filtro = (
                Q(titulo__icontains=palabra) |
                Q(isbn__icontains=palabra) |
                Q(escribe__idautor__nombre__icontains=palabra) |
                Q(pertenece__idcategoria__nombre__icontains=palabra)
            )
            filtros_palabras.append(filtro)

        return queryset.filter(reduce(operator.and_, filtros_palabras)).distinct()
    
    def _anotar_estado_usuario(self, queryset):
        correo_usuario = self.request.session.get('correo_usuario')
        
        if not correo_usuario:
            return queryset.annotate(ya_lo_tiene=Q(pk__in=[]), solicitud_pendiente=Q(pk__in=[]))

        # Atributos exactos del MR: codigo y correo
        cliente = Cliente.objects.filter(codigo__correo=correo_usuario).first()
        
        if cliente and cliente.rol.lower() == 'estudiante':
            # USANDO 'isbn' EXACTO DEL MODELO (no isbn_id)
            libros_solicitados = Solicitudprestamo.objects.filter(
                codigo_c=cliente, estado='pendiente'
            ).values_list('isbn', flat=True)
            
            # USANDO 'isbn' EXACTO DEL MODELO (no isbn_id)
            libros_prestados = Prestamo.objects.filter(
                idsolicitud__codigo_c=cliente, devolucion__isnull=True
            ).values_list('idsolicitud__isbn', flat=True)
            
            return queryset.annotate(
                solicitud_pendiente=Q(isbn__in=libros_solicitados),
                ya_lo_tiene=Q(isbn__in=libros_prestados)
            )
            
        return queryset.annotate(ya_lo_tiene=Q(pk__in=[]), solicitud_pendiente=Q(pk__in=[]))

    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()

        # 1. Consulta base con el conteo de ejemplares físicos disponibles
        queryset = Libro.objects.annotate(
            disponibles_count=Count('ejemplar', filter=Q(ejemplar__estado__iexact='disponible'))
        )

        # 2. Delegar la búsqueda al método independiente
        queryset = self._aplicar_filtro_busqueda(queryset, q)

        # 3. Delegar la información de sesión al método independiente
        queryset = self._anotar_estado_usuario(queryset)

        # 4. Retornar el resultado final ordenado
        return queryset.order_by('-disponibles_count', 'titulo')

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')
        usuario = Usuario.objects.filter(correo=correo).first()

        if usuario is None:
            return render(request, 'core/login.html', {'error': 'Usuario o contraseña incorrectos'})

        if usuario.contrasenia != contrasenia:
            return render(request, 'core/login.html', {'error': 'Usuario o contraseña incorrectos'})
        if Admin.objects.filter(codigo=usuario.codigo).exists():
            rol = 'admin'
        else:
            cliente = Cliente.objects.filter(codigo=usuario.codigo).first()
            if cliente is not None:
                rol = cliente.rol
            else:
                return render(request, 'core/login.html', {'error': 'Usuario sin rol asignado'})
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
        usuario = Usuario.objects.create(codigo=codigo,identificacion=identificacion,nombre=nombre,correo=correo,contrasenia=contrasenia)
        Cliente.objects.create(codigo=usuario,rol=rol,carrera=carrera,estado='activo')
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
        cliente = Cliente.objects.filter(codigo__correo=correo_usuario).first()

        if not cliente or cliente.estado.upper() != 'ACTIVO':
            messages.error(request, 'Tu cuenta se encuentra bloqueada.')
            return redirect('libros')

        if cliente.rol.lower() == 'estudiante':
            solicitud_pendiente = Solicitudprestamo.objects.filter(codigo_c=cliente,isbn=libro,estado='pendiente').exists()

            if solicitud_pendiente:
                return redirect('libros')

        if cliente.rol.lower() == 'estudiante':
            ya_lo_tiene = Prestamo.objects.filter(idsolicitud__codigo_c=cliente,idsolicitud__isbn=libro,devolucion__isnull=True).exists()

            if ya_lo_tiene:
                return redirect('libros')
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
    if request.session.get('rol') != 'admin':
        return redirect('libros')

    # Solicitudes pendientes y gestionadas
    pendientes = Solicitudprestamo.objects.filter(estado='pendiente').select_related('isbn', 'codigo_c').annotate(disponibles_count=Count('isbn__ejemplar',filter=Q(isbn__ejemplar__estado='disponible'))).order_by('-idsolicitud')
    gestionadas = Solicitudprestamo.objects.filter(estado__in=['aprobado', 'rechazado']).select_related('isbn', 'codigo_c').order_by('-idsolicitud')

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
            Prestamo.objects.create(idprestamo=id_prestamo,idsolicitud=solicitud,codigobarras=ejemplar,fechaprestamo=hoy,fechavencimiento=vencimiento)
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
        autores_seleccionados = list(
            dict.fromkeys(idautor
                for idautor in request.POST.getlist('autores')
                if idautor
            )
        )
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
        return render(request, 'core/form_libro.html', {'libro': libro,'editoriales': editoriales,'autores': autores,'autores_actuales': list(Escribe.objects.filter(isbn=libro).values_list('idautor_id', flat=True)),'cantidad_ejemplares': Ejemplar.objects.filter(isbn=libro).count(),'accion': 'Editar','error': mensaje})

    if request.method == 'POST':
        libro.ideditorial_id = request.POST.get('ideditorial')
        libro.titulo = request.POST.get('titulo', '').strip()
        libro.anio = request.POST.get('anio')
        libro.descripcion = request.POST.get('descripcion')
        autores_seleccionados = list(
            dict.fromkeys(idautor
                for idautor in request.POST.getlist('autores')
                if idautor
            )
        )
        imagen = request.FILES.get('imagen')

        agregar_ejemplares = (request.POST.get('agregar_ejemplares') == 'on')
        ejemplares_actuales = list(Ejemplar.objects.filter(isbn=libro).order_by('codigobarras'))

        ubicaciones_nuevas = []
        diferencia = 0

        if agregar_ejemplares:
            try:
                cantidad_nueva = int(request.POST.get('cantidad_ejemplares', ''))
            except (ValueError, TypeError):
                return mostrar_error('La cantidad de ejemplares debe ser un número entero.')

            if cantidad_nueva < 1 or cantidad_nueva > 999:
                return mostrar_error('La cantidad debe estar entre 1 y 999.')

            ubicacion = request.POST.get('ubicacion', '').strip()
            autorrellenar = (request.POST.get('autorrellenar_ubicaciones') == 'on')

            if not re.fullmatch(r'[A-Z][0-9]{2}', ubicacion):
                return mostrar_error('La ubicación debe tener una letra mayúscula ''y dos números. Ejemplo: A03.')
            numero_inicial = int(ubicacion[1:])

            if autorrellenar and numero_inicial + cantidad_nueva - 1 > 99:
                return mostrar_error('Las ubicaciones generadas superarían el formato ''de dos dígitos. Elige otra ubicación o desactiva ''el autorrellenado.')

            if autorrellenar:
                letra = ubicacion[0]
                ubicaciones_nuevas = [f'{letra}{numero_inicial + i:02d}'for i in range(cantidad_nueva)]
            else:
                ubicaciones_nuevas = [ubicacion] * cantidad_nueva
            diferencia = cantidad_nueva
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



def eliminar_libro_view(request, pk):
    if request.session.get('rol') != 'admin':
        return redirect('libros')

    if request.method != 'POST':
        return redirect('libros')
    libro = get_object_or_404(Libro, pk=pk)

    # Comprobar si algún ejemplar está prestado.
    if Ejemplar.objects.filter(isbn=libro,estado__iexact='prestado').exists():
        messages.error(request,f'No se puede eliminar "{libro.titulo}" porque ''tiene ejemplares prestados.')
        return redirect('libros')

    tiene_solicitudes = Solicitudprestamo.objects.filter(isbn=libro).exists()
    tiene_prestamos = Prestamo.objects.filter(codigobarras__isbn=libro).exists()
    tiene_devoluciones = Devolucion.objects.filter(idprestamo__codigobarras__isbn=libro).exists()

    if tiene_solicitudes or tiene_prestamos or tiene_devoluciones:
        try:
            with transaction.atomic():
                ejemplares = Ejemplar.objects.filter(isbn=libro)
                ejemplares_con_prestamos = Prestamo.objects.filter(codigobarras__isbn=libro).values_list('codigobarras_id', flat=True)
                ejemplares.filter(codigobarras__in=ejemplares_con_prestamos).update(estado='BORRADO')
                ejemplares.exclude(codigobarras__in=ejemplares_con_prestamos).delete()

            messages.success(request,f'"{libro.titulo}" tiene solicitudes o historial. ''Se conservaron el libro y su portada, y se ''retiraron sus ejemplares.')
        except Exception:
            messages.error(request,'No se pudieron retirar los ejemplares del libro.')
        return redirect('libros')

    try:
        with transaction.atomic():
            Escribe.objects.filter(isbn=libro).delete()
            Ejemplar.objects.filter(isbn=libro).delete()
            libro.delete()

    except Exception:
        messages.error(request,'No se pudo eliminar el libro por sus relaciones ''con otros registros.')
        return redirect('libros')

    # Borrar la portada física
    if libro.url_imagen and libro.url_imagen.startswith('/media/Libros/'):
        nombre_imagen = os.path.basename(libro.url_imagen)
        ruta_imagen = os.path.join(settings.MEDIA_ROOT,'Libros',nombre_imagen)

        if os.path.isfile(ruta_imagen):
            os.remove(ruta_imagen)

    messages.success(request,f'El libro "{libro.titulo}" se eliminó correctamente.')
    return redirect('libros')



def gestionar_usuarios_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
    
    usuarios = Usuario.objects.all().order_by('nombre')
    admins_ids = set(Admin.objects.values_list('codigo_id', flat=True))
    
    # Creamos un diccionario de clientes para cruzar los datos rápido en memoria
    clientes_dict = {c.codigo_id: c for c in Cliente.objects.all()}
    
    usuarios_data = []
    for u in usuarios:
        usuarios_data.append({
            'usuario': u,
            'is_admin': u.codigo in admins_ids,
            'cliente': clientes_dict.get(u.codigo)
        })
        
    return render(request, 'core/gestionar_usuarios.html', {'usuarios_data': usuarios_data})


def cambiar_permiso_admin_view(request, codigo_usuario):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
        
    usuario = get_object_or_404(Usuario, codigo=codigo_usuario)
    admin_existente = Admin.objects.filter(codigo=usuario).first()
    
    if admin_existente:
        try:
            admin_existente.delete()
            messages.success(request, f"Se revocaron los permisos de administrador a {usuario.nombre}.")
        except IntegrityError:
            # Capturamos el error de PostgreSQL para que no explote la app
            messages.error(
                request, 
                f"No se pueden revocar los permisos a {usuario.nombre} porque ya ha gestionado préstamos o devoluciones. El sistema requiere conservar su historial de auditoría."
            )
    else:
        Admin.objects.create(codigo=usuario)
        messages.success(request, f"{usuario.nombre} ahora es administrador.")
        
    return redirect('gestionar_usuarios')


def cambiar_estado_usuario_view(request, pk):
    if request.session.get('rol') != 'admin':
        return redirect('principal')
        
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, codigo_id=pk)
        
        if cliente.estado.lower() == 'activo':
            cliente.estado = 'bloqueado'
        else:
            cliente.estado = 'activo'
            
        cliente.save(update_fields=['estado'])
        messages.success(request, f"El estado de {cliente.codigo.nombre} cambió a {cliente.estado.upper()}.")
        
    return redirect('gestionar_usuarios')


def procesar_devoluciones_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
    # Préstamos que aún no tienen un registro de devolución asociado
    prestamos_activos = Prestamo.objects.filter(devolucion__isnull=True)

    context = {'prestamos': prestamos_activos}
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
        Devolucion.objects.create(iddevolucion=id_devolucion,idprestamo=prestamo,codigo=admin_obj,fechadevolucion=hoy,observaciones=observaciones,multa=multa)

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


def registrar_autor_view(request):
    if request.session.get('rol') != 'admin':
        return redirect('libros')

    libros = Libro.objects.all().order_by('titulo')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        libros_seleccionados = request.POST.getlist('libros')

        if not nombre:
            return render(request, 'core/form_autor.html', {'error': 'El nombre del autor es obligatorio.','libros': libros})

        ids_existentes = Autor.objects.values_list('idautor', flat=True)
        numeros_usados = []

        for idautor in ids_existentes:
            coincidencia = re.fullmatch(r'AUT(\d+)', idautor, re.IGNORECASE)

            if coincidencia:
                numeros_usados.append(int(coincidencia.group(1)))
        siguiente_numero = max(numeros_usados, default=0) + 1
        nuevo_id = f'AUT{siguiente_numero:03d}'

        while Autor.objects.filter(idautor=nuevo_id).exists():
            siguiente_numero += 1
            nuevo_id = f'AUT{siguiente_numero:03d}'

        with transaction.atomic():
            autor = Autor.objects.create(idautor=nuevo_id,nombre=nombre)
            libros_validos = Libro.objects.filter(isbn__in=libros_seleccionados)

            for libro in libros_validos:
                Escribe.objects.create(isbn=libro,idautor=autor)
        messages.success(request,f'Autor Agregado\n'f'Id: {nuevo_id}\n'f'Nombre: {nombre}')
        return redirect('registrar_autor')
    return render(request, 'core/form_autor.html', {'libros': libros})




def gestionar_ejemplares_view(request, pk=None):
    if request.session.get('rol') != 'admin':
        return redirect('libros')
    libros = Libro.objects.all().order_by('titulo')

    if pk is not None:
        libro = get_object_or_404(Libro, pk=pk)
    else:
        libro = None

    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad_ejemplares', ''))
        except (ValueError, TypeError):
            cantidad = 0

        ubicacion = request.POST.get('ubicacion', '').strip()
        autorrellenar = (request.POST.get('autorrellenar_ubicaciones') == 'on')

        if cantidad < 1 or cantidad > 999:
            messages.error(request,'La cantidad debe estar entre 1 y 999.')
            return redirect('gestionar_ejemplares', pk=libro.pk)

        if not re.fullmatch(r'[A-Z][0-9]{2}', ubicacion):
            messages.error(request,'La ubicación debe tener una letra mayúscula ''y dos números. Ejemplo: A03.')
            return redirect('gestionar_ejemplares', pk=libro.pk)

        numero_inicial = int(ubicacion[1:])

        if autorrellenar and numero_inicial + cantidad - 1 > 99:
            messages.error(request,'Las ubicaciones generadas superarían el formato ''de dos dígitos. Elige otra ubicación inicial ''o desactiva el autorrellenado.')
            return redirect('gestionar_ejemplares', pk=libro.pk)

        if autorrellenar:
            letra = ubicacion[0]
            ubicaciones = [f'{letra}{numero_inicial + i:02d}'for i in range(cantidad)]
        else:
            ubicaciones = [ubicacion] * cantidad

        with transaction.atomic():
            codigos_existentes = set(Ejemplar.objects.values_list('codigobarras', flat=True))
            numeros_usados = []

            for codigo in codigos_existentes:
                coincidencia = re.fullmatch(r'EJ(\d+)', codigo, re.IGNORECASE)

                if coincidencia:
                    numeros_usados.append(int(coincidencia.group(1)))

            siguiente_numero = max(numeros_usados, default=0) + 1

            for ubicacion_ejemplar in ubicaciones:
                while f'EJ{siguiente_numero:03d}' in codigos_existentes:
                    siguiente_numero += 1
                codigo_barras = f'EJ{siguiente_numero:03d}'
                Ejemplar.objects.create(codigobarras=codigo_barras,isbn=libro,ubicacion=ubicacion_ejemplar,estado='disponible')

                codigos_existentes.add(codigo_barras)
                siguiente_numero += 1

        messages.success(request,f'Se agregaron {cantidad} ejemplar(es) a "{libro.titulo}".')
        return redirect('gestionar_ejemplares', pk=libro.pk)
    ejemplares = (
        Ejemplar.objects.filter(isbn=libro).order_by('codigobarras')
        if libro is not None
        else Ejemplar.objects.none())
    return render(request,'core/gestionar_ejemplares.html',{'libro': libro,'libros': libros,'ejemplares': ejemplares,})



def borrar_ejemplar_view(request, pk, codigo):
    if request.session.get('rol') != 'admin':
        return redirect('libros')

    if request.method != 'POST':
        return redirect('gestionar_ejemplares', pk=pk)

    libro = get_object_or_404(Libro, pk=pk)
    ejemplar = get_object_or_404(Ejemplar,codigobarras=codigo,isbn=libro)
    prestamos = Prestamo.objects.filter(codigobarras=ejemplar)

    if prestamos.filter(
        devolucion__isnull=True).exists():
        messages.error(request,f'No se puede borrar el ejemplar {codigo}: ''tiene un préstamo sin devolución registrada.')
        return redirect('gestionar_ejemplares', pk=libro.pk)

    if prestamos.exists():
        ejemplar.estado = 'BORRADO'
        ejemplar.save(update_fields=['estado'])
        messages.success(request,f'El ejemplar {codigo} se marcó como BORRADO. ''Su historial se conserva.')
    else:
        ejemplar.delete()
        messages.success(request,f'El ejemplar {codigo} se eliminó correctamente.')
    return redirect('gestionar_ejemplares', pk=libro.pk)

