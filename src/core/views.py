import os
import re
import operator
from functools import reduce
import datetime
from datetime import date
from django.db import models
import uuid
import json

from .models import Libro, Usuario, Admin, Cliente, Ejemplar, Solicitudprestamo, Prestamo, Editorial, Devolucion, Autor, Escribe, Pertenece, Categoria
from .reglas import calcular_multa

from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Count, Q, Sum
from django.contrib import messages
from django.conf import settings
from django.db import transaction, IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.hashers import identify_hasher





def es_admin_activo(request):
    correo = request.session.get('correo_usuario')
    if not correo:
        return False
    usuario = Usuario.objects.filter(correo=correo).first()

    if usuario is None:
        return render(request,'core/login.html',{'error': 'Usuario o contraseña incorrectos'})

    if usuario is None:
        request.session.flush()
        return False

    # Consultar el estado actual del administrador
    admin = Admin.objects.filter(codigo=usuario.codigo,activo=True).first()

    if admin:
        # Actualizar la sesión
        request.session['rol'] = 'admin'
        return True

    # Recuperar su rol de cliente
    cliente = Cliente.objects.filter(codigo=usuario.codigo).first()

    if cliente:
        request.session['rol'] = cliente.rol
    else:
        # Ya no tiene ningún rol asignado
        request.session.flush()

    return False




def sincronizar_rol(request):
    correo = request.session.get('correo_usuario')
    if not correo:
        return

    usuario = Usuario.objects.filter(correo=correo).first()

    if not usuario:
        request.session.flush()
        return
    admin = Admin.objects.filter(codigo=usuario.codigo,activo=True).exists()

    if admin:
        request.session['rol'] = 'admin'
        return
    cliente = Cliente.objects.filter(codigo=usuario.codigo).first()

    if cliente:
        actualizar_morosidad_cliente(cliente)
        request.session['rol'] = cliente.rol
    else:
        request.session.flush()


def actualizar_morosidad_cliente(cliente):
    if not cliente or cliente.rol.lower() not in ['estudiante', 'docente']:
        return

    hoy = date.today()

    multas_registradas = Devolucion.objects.filter(
        idprestamo__idsolicitud__codigo_c=cliente,
        pagado=False
    ).aggregate(total=Sum('multa'))['total'] or 0

    prestamos_vencidos_activos = Prestamo.objects.filter(
        idsolicitud__codigo_c=cliente,
        devolucion__isnull=True,
        fechavencimiento__lt=hoy
    )

    multas_activas = 0
    for prestamo in prestamos_vencidos_activos:
        multas_activas += calcular_multa(prestamo.fechavencimiento, hoy)

    deuda_total_actual = multas_registradas + multas_activas

    if deuda_total_actual > 50000 and cliente.estado == 'activo':
        cliente.estado = 'bloqueado'
        cliente.save(update_fields=['estado'])

    elif deuda_total_actual <= 50000 and cliente.estado == 'bloqueado':
        cliente.estado = 'activo'
        cliente.save(update_fields=['estado'])

class LibroListView(ListView):
    def dispatch(self, request, *args, **kwargs):
        sincronizar_rol(request)
        return super().dispatch(request, *args, **kwargs)
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
        disponibilidad = self.request.GET.get('disponibilidad', 'todos')
        categoria_id = self.request.GET.get('categoria_id', '').strip()
        autor_id = self.request.GET.get('autor_id', '').strip()

        # 1. Contar los ejemplares disponibles de cada libro
        queryset = Libro.objects.annotate(disponibles_count=Count('ejemplar',filter=Q(ejemplar__estado__iexact='disponible')))

        # 2. Aplicar la búsqueda por texto
        queryset = self._aplicar_filtro_busqueda(queryset, q)

        # 3. Filtrar por la categoría seleccionada
        if categoria_id:
            queryset = queryset.filter(pertenece__idcategoria_id=categoria_id).distinct()

        # 4. Filtrar por el autor seleccionado
        if autor_id:
            queryset = queryset.filter(escribe__idautor_id=autor_id).distinct()

        # 5. Filtrar por disponibilidad
        if disponibilidad == 'disponibles':
            queryset = queryset.filter(disponibles_count__gt=0)
        elif disponibilidad == 'agotados':
            queryset = queryset.filter(disponibles_count=0)

        # 6. Conservar la información del usuario
        queryset = self._anotar_estado_usuario(queryset)

        # 7. Ordenar los resultados
        return queryset.order_by('-disponibles_count', 'titulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for libro in context['libros']:
            libro.categorias = Pertenece.objects.filter(isbn=libro).select_related('idcategoria')
        return context



def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')
        usuario = Usuario.objects.filter(correo=correo).first()

        # Comprobar si la contraseña almacenada ya tiene formato de hash
        try:
            identify_hasher(usuario.contrasenia)
            es_hash = True
        except ValueError:
            es_hash = False

        if es_hash:
            # Cuenta con contraseña protegida mediante hash
            if not check_password(contrasenia, usuario.contrasenia):
                return render(request,'core/login.html',{'error': 'Usuario o contraseña incorrectos'})
        else:
            # Cuenta antigua: contraseña guardada como texto
            if usuario.contrasenia != contrasenia:
                return render(request,'core/login.html',{'error': 'Usuario o contraseña incorrectos'})
            # Actualizar la contraseña al formato seguro tras iniciar sesión
            usuario.contrasenia = make_password(contrasenia)
            usuario.save(update_fields=['contrasenia'])

        admin = Admin.objects.filter(codigo=usuario.codigo).first()

        if admin and admin.activo:
            rol = 'admin'
        else:
            cliente = Cliente.objects.filter(codigo=usuario.codigo).first()

            if cliente is not None:
                rol = cliente.rol
            else:
                return render(request, 'core/login.html', {'error': 'Usuario sin rol asignado'})
        request.session['rol'] = rol
        request.session['correo_usuario'] = usuario.correo
        request.session['nombre'] = usuario.nombre.split()[0]
        return redirect('inicio')
    return render(request, 'core/login.html')


def inicio_view(request):
    sincronizar_rol(request)
    return render(request, 'core/principal.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')



def registro_view(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        identificacion = request.POST.get('identificacion', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        correo = request.POST.get('correo', '').strip()
        contrasenia = request.POST.get('contrasenia', '')
        rol = request.POST.get('rol', '').strip()
        carrera = request.POST.get('carrera', '').strip()

        def mostrar_error(mensaje):
            return render(request, 'core/registro.html', {'error': mensaje})

        # Validar el correo electrónico
        try:
            validate_email(correo)
        except ValidationError:
            return mostrar_error('Ingresa una dirección de correo electrónico válida.')

        if len(correo) > 100:
            return mostrar_error('El correo no puede superar los 100 caracteres.')

        # Validar código institucional: exactamente 9 cifras
        if not re.fullmatch(r'[0-9]{9}', codigo):
            return mostrar_error('El código institucional debe contener exactamente 9 cifras.')

        # Validar formato numérico de CC/TI
        if not re.fullmatch(r'[0-9]{6,10}', identificacion):
            return mostrar_error('La identificación debe contener entre 6 y 10 cifras.')

        # Validar nombre: letras, espacios, apóstrofes y guiones
        patron_nombre = (r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+" r"([ '-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*")

        if not re.fullmatch(patron_nombre, nombre):
            return mostrar_error('El nombre solo puede contener letras, espacios, ' 'apóstrofes y guiones.')

        if len(nombre) > 60:
            return mostrar_error('El nombre no puede superar los 60 caracteres.')

        # Evitar códigos, identificaciones y correos duplicados
        if Usuario.objects.filter(codigo=codigo).exists():
            return mostrar_error('Ese código institucional ya está registrado.')

        if Usuario.objects.filter(identificacion=identificacion).exists():
            return mostrar_error('Esa identificación ya está registrada.')

        if Usuario.objects.filter(correo=correo).exists():
            return mostrar_error('Ese correo electrónico ya está registrado.')

        # Validar el rol permitido
        if rol not in ['estudiante', 'docente']:
            return mostrar_error('Debes seleccionar un rol válido.')


        if not contrasenia:
            return mostrar_error('La contraseña es obligatoria.')

        if len(contrasenia) < 8:
            return mostrar_error('La contraseña debe tener al menos 8 caracteres.')

        if len(contrasenia) > 100:
            return mostrar_error('La contraseña no puede superar los 100 caracteres.')


        # Crear el usuario y su registro de cliente
        try:
            with transaction.atomic():
                usuario = Usuario.objects.create(codigo=codigo,identificacion=identificacion,nombre=nombre,correo=correo,contrasenia=make_password(contrasenia))

                Cliente.objects.create(codigo=usuario,rol=rol,carrera=carrera,estado='activo')

        except IntegrityError:
            return mostrar_error('No se pudo completar el registro porque alguno de los datos ' 'ya está registrado o no cumple las restricciones de la base de datos.')
        return redirect('login')

    return render(request, 'core/registro.html')



# Views para visualizacion de prestamos y solicitudes


def solicitar_prestamo_view(request, pk):
    sincronizar_rol(request)
    libro = get_object_or_404(Libro, pk=pk)

    if request.session.get('rol') not in ['estudiante', 'docente']:
        if not request.session.get('rol'):
            return redirect('login')
        return redirect('inicio')

    if request.method == 'POST':
        correo_usuario = request.session.get('correo_usuario')
        cliente = Cliente.objects.filter(codigo__correo=correo_usuario).first()

        if not cliente:
            messages.error(request, 'No se encontró tu cuenta.')
            return redirect('inicio')
        
        if cliente.estado == 'bloqueado':
            messages.error(request, 'Tu cuenta está bloqueada. Comunícate con la administración.')
            return redirect('inicio')
        
        total_multas = Devolucion.objects.filter(idprestamo__idsolicitud__codigo_c=cliente,pagado=False,multa__gt=0).aggregate(total=models.Sum('multa'))['total'] or 0

        if total_multas > 0:
            messages.error(
                request,
                'Tu cuenta se encuentra bloqueada porque tienes multas pendientes.'
            )
            return redirect('inicio')
        
        if total_multas > 0:
            messages.error(request,'Tu cuenta se encuentra bloqueada porque tienes multas pendientes.')
            return redirect('inicio')


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
        ids_existentes = Solicitudprestamo.objects.values_list('idsolicitud',flat=True)
        numeros_usados = []

        for id_solicitud in ids_existentes:
            coincidencia = re.fullmatch(r'SOL(\d+)', id_solicitud)

            if coincidencia:
                numeros_usados.append(int(coincidencia.group(1)))
        siguiente_numero = max(numeros_usados, default=0) + 1
        id_sol = f'SOL{siguiente_numero:03d}'

        while Solicitudprestamo.objects.filter(idsolicitud=id_sol).exists():
            siguiente_numero += 1
            id_sol = f'SOL{siguiente_numero:03d}'
        Solicitudprestamo.objects.create(idsolicitud=id_sol,codigo_c=cliente,isbn=libro,estado='pendiente')
        return redirect('libros')
    context = {'libro': libro,}
    return render(request, 'core/solicitar_prestamo.html', context)


def mis_prestamos_view(request):
    sincronizar_rol(request)
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
    if request.method != 'POST':
        return redirect('mis_prestamos')

    correo_usuario = request.session.get('correo_usuario')
    if not correo_usuario:
        return redirect('login')

    solicitud = get_object_or_404(Solicitudprestamo, idsolicitud=pk)

    if solicitud.codigo_c.codigo.correo != correo_usuario and not es_admin_activo(request):
        messages.error(request, 'No tienes permiso para anular esta solicitud.')
        return redirect('mis_prestamos')

    if solicitud.estado != 'pendiente':
        messages.error(request, 'No puedes cancelar una solicitud que ya fue aprobada o rechazada.')
        return redirect('mis_prestamos')

    solicitud.delete()
    messages.success(request, 'Solicitud cancelada y eliminada correctamente.')
    return redirect('mis_prestamos')


def gestionar_solicitudes_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')
    
    # Solicitudes pendientes y gestionadas
    pendientes = Solicitudprestamo.objects.filter(estado='pendiente').select_related('isbn', 'codigo_c').annotate(disponibles_count=Count('isbn__ejemplar',filter=Q(isbn__ejemplar__estado='disponible'))).order_by('-idsolicitud')
    gestionadas = Solicitudprestamo.objects.filter(estado__in=['aprobado', 'rechazado']).select_related('isbn', 'codigo_c').order_by('-idsolicitud')

    context = {
        'pendientes': pendientes,
        'gestionadas': gestionadas,
    }
    return render(request, 'core/gestionar_solicitudes.html', context)


def cambiar_estado_solicitud_view(request, pk, accion):
    if not es_admin_activo(request):
        return redirect('inicio')
    
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
            ids_existentes = Prestamo.objects.values_list('idprestamo',flat=True)
            numeros_usados = []

            for id_existente in ids_existentes:
                coincidencia = re.fullmatch(r'PRE(\d+)', id_existente)

                if coincidencia:
                    numeros_usados.append(int(coincidencia.group(1)))

            siguiente_numero = max(numeros_usados, default=0) + 1
            id_prestamo = f'PRE{siguiente_numero:03d}'

            while Prestamo.objects.filter(idprestamo=id_prestamo).exists():
                siguiente_numero += 1
                id_prestamo = f'PRE{siguiente_numero:03d}'

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
    if not es_admin_activo(request):
        return redirect('inicio')
    
    editoriales = Editorial.objects.all()
    autores = Autor.objects.all().order_by('nombre')

    if request.method == 'POST':
        isbn = request.POST.get('isbn', '').strip()
        ideditorial_id = request.POST.get('ideditorial')
        titulo = request.POST.get('titulo', '').strip()
        anio = request.POST.get('anio')
        descripcion = request.POST.get('descripcion')

        descripcion = (descripcion or '').strip()

        # Validar ISBN
        if not isbn:
            return mostrar_error('El ISBN es obligatorio.')

        if len(isbn) > 20:
            return mostrar_error('El ISBN no puede superar los 20 caracteres.')
        if not isbn_valido(isbn):
            return mostrar_error('El ISBN no es válido. Debe ser un ISBN-10 o ISBN-13 correcto.')

        if Libro.objects.filter(isbn=isbn).exists():
            return mostrar_error('Ya existe un libro con ese ISBN.')

        # Validar título
        if not titulo:
            return mostrar_error('El título es obligatorio.')

        if len(titulo) > 100:
            return mostrar_error('El título no puede superar los 100 caracteres.')

        # Validar año
        try:
            anio = int(anio)
        except (ValueError, TypeError):
            return mostrar_error('El año debe ser un número entero.')

        if anio < 1 or anio > timezone.localdate().year:
            return mostrar_error(f'El año debe estar entre 1 y {timezone.localdate().year}.')

        # Validar descripción
        if len(descripcion) > 1000:
            return mostrar_error('La descripción no puede superar los 1000 caracteres.')



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
        print("DEBUG:", repr(cantidad_texto), repr(ubicacion), request.POST.get('cantidad_ejemplares'))

        def mostrar_error(mensaje):
            return render(request, 'core/form_libro.html', {'editoriales': editoriales,'autores': autores,'accion': 'Registrar', 'categorias': Categoria.objects.all(),'error': mensaje})
        cantidad = 0
        ubicaciones = []

        if cantidad_texto.strip():
            try:
                cantidad = int(cantidad_texto)
            except (ValueError, TypeError):
                return mostrar_error('La cantidad de ejemplares debe ser un número entero.')

        if cantidad > 0:
            if cantidad > 999:
                return mostrar_error('La cantidad debe estar entre 1 y 999.')

            if not re.fullmatch(r'[A-Z][0-9]{2}', ubicacion):
                return mostrar_error('La ubicación debe tener una letra mayúscula ''y dos números. Ejemplo: A03.')

            if autorrellenar and int(ubicacion[1:]) + cantidad - 1 > 99:
                return mostrar_error('Las ubicaciones generadas superarían el formato ''de dos dígitos. Elige otra ubicación inicial ''o desactiva el autorrellenado.')

            if autorrellenar:
                letra = ubicacion[0]
                numero_inicial = int(ubicacion[1:])

                for i in range(cantidad):
                    ubicaciones.append(f'{letra}{numero_inicial + i:02d}')
            else:
                ubicaciones = [ubicacion] * cantidad

        extension = None
        if imagen:
            extension = os.path.splitext(imagen.name)[1].lower()
            if extension not in ['.jpg', '.jpeg', '.png', '.webp']:
                return mostrar_error('Formato no permitido. Usa JPG, JPEG, PNG o WEBP.')

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
        'categorias': Categoria.objects.all().order_by('nombre'),
        'accion': 'Registrar'
    }

    return render(request, 'core/form_libro.html', context)



def editar_libro_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')

    libro = get_object_or_404(Libro, pk=pk)
    editoriales = Editorial.objects.all()
    autores = Autor.objects.all().order_by('nombre')
    categorias = Categoria.objects.all().order_by('nombre')

    def mostrar_error(mensaje):
        return render(request, 'core/form_libro.html', {
            'libro': libro,
            'editoriales': editoriales,
            'autores': autores,
            'categorias': categorias,
            'autores_actuales': list(Escribe.objects.filter(isbn=libro).values_list('idautor_id', flat=True)),
            'categorias_actuales': list(Pertenece.objects.filter(isbn=libro).values_list('idcategoria_id', flat=True)),
            'cantidad_ejemplares': Ejemplar.objects.filter(isbn=libro).count(),
            'accion': 'Editar',
            'error': mensaje
        })

    if request.method == 'POST':
        libro.ideditorial_id = request.POST.get('ideditorial')
        libro.titulo = request.POST.get('titulo', '').strip()
        libro.anio = request.POST.get('anio')
        libro.descripcion = request.POST.get('descripcion')

        
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        anio_texto = request.POST.get('anio', '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()

        # Validar el título
        if not titulo:
            return mostrar_error('El título es obligatorio.')

        if len(titulo) > 100:
            return mostrar_error('El título no puede superar los 100 caracteres.')

        # Validar el ISBN existente
        if not libro.isbn or len(libro.isbn) > 20:
            return mostrar_error('El ISBN debe tener máximo 20 caracteres.')

        # Validar el año
        try:
            anio = int(anio_texto)
        except (ValueError, TypeError):
            return mostrar_error('El año debe ser un número entero.')

        if anio < 1 or anio > timezone.localdate().year:
            return mostrar_error(f'El año debe estar entre 1 y {timezone.localdate().year}.')

        # Validar la descripción
        if len(descripcion) > 1000:
            return mostrar_error('La descripción no puede superar los 1000 caracteres.')

        # Asignar los datos después de validar
        libro.ideditorial_id = request.POST.get('ideditorial')
        libro.titulo = titulo
        libro.anio = anio
        libro.descripcion = descripcion or None


        autores_seleccionados = list(
            dict.fromkeys(idautor
                for idautor in request.POST.getlist('autores')
                if idautor
            )
        )

        categorias_seleccionadas = list(dict.fromkeys(idcategoria
            for idcategoria in request.POST.getlist('categorias')
            if idcategoria
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

            # Actualizar autores
            Escribe.objects.filter(isbn=libro).delete()

            for idautor in autores_seleccionados:
                Escribe.objects.create(isbn=libro,idautor_id=idautor)

            # Actualizar categorías
            Pertenece.objects.filter(isbn=libro).delete()

            for idcategoria in categorias_seleccionadas:
                Pertenece.objects.create(isbn=libro,idcategoria_id=idcategoria)





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
    categorias_actuales = list(Pertenece.objects.filter(isbn=libro).values_list('idcategoria_id', flat=True))

    context = {
        'libro': libro,
        'editoriales': editoriales,
        'autores': autores,
        'categorias': categorias,
        'autores_actuales': autores_actuales,
        'categorias_actuales': categorias_actuales,
        'cantidad_ejemplares': cantidad_ejemplares,
        'accion': 'Editar'
    }
    return render(request, 'core/form_libro.html', context)



def eliminar_libro_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')

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
    sincronizar_rol(request)

    if not es_admin_activo(request):
        return redirect('inicio')
    usuarios = Usuario.objects.all().order_by('nombre')
    admins = {admin.codigo_id: admin for admin in Admin.objects.all()}
    clientes_dict = {cliente.codigo_id: cliente for cliente in Cliente.objects.all()}

    busqueda = request.GET.get('q', '').strip()
    filtro_rol = request.GET.get('rol', '')
    filtro_estado = request.GET.get('estado', '')
    filtro_privilegios = request.GET.get('privilegios', '')
    filtro_prestamos = request.GET.get('prestamos', '')

    usuarios_data = []

    for usuario in usuarios:
        admin = admins.get(usuario.codigo)
        cliente = clientes_dict.get(usuario.codigo)

        admin_activo = admin is not None and admin.activo
        tiene_registro_admin = admin is not None

        # Búsqueda por código, nombre o correo
        if busqueda:
            texto_busqueda = busqueda.lower()
            coincide = (texto_busqueda in str(usuario.codigo).lower() or texto_busqueda in (usuario.nombre or '').lower() or texto_busqueda in (usuario.correo or '').lower())
            if not coincide:
                continue

        if filtro_rol == 'admin' and not admin_activo:
            continue
        if filtro_rol == 'cliente' and cliente is None:
            continue
        if filtro_rol == 'sin_rol' and cliente is not None:
            continue

        if filtro_estado:
            if cliente is None:
                continue
            estado_cliente = (cliente.estado or '').lower()
            if filtro_estado == 'activo' and estado_cliente != 'activo':
                continue
            if filtro_estado == 'bloqueado' and estado_cliente != 'bloqueado':
                continue

        if filtro_privilegios == 'activo' and not admin_activo:
            continue
        if filtro_privilegios == 'inactivo':
            if not tiene_registro_admin or admin_activo:
                continue
        if filtro_privilegios == 'ninguno' and tiene_registro_admin:
            continue

        if filtro_prestamos:
            if cliente is None:
                continue
            tiene_prestamos = Prestamo.objects.filter(codigo_c=cliente).exists()
            if filtro_prestamos == 'con' and not tiene_prestamos:
                continue
            if filtro_prestamos == 'sin' and tiene_prestamos:
                continue

        usuarios_data.append({
            'usuario': usuario,
            'cliente': cliente,
            'is_admin': admin_activo,
            'tiene_registro_admin': tiene_registro_admin,
            'admin_activo': admin_activo,
        })

    # Orden: administradores activos, administradores inactivos, demás usuarios
    usuarios_data.sort(
        key=lambda item: (
            0 if item['admin_activo']
            else 1 if item['tiene_registro_admin']
            else 2,
            (item['usuario'].nombre or '').lower()
        )
    )

    context = {
        'usuarios_data': usuarios_data,
        'busqueda': busqueda,
        'filtro_rol': filtro_rol,
        'filtro_estado': filtro_estado,
        'filtro_privilegios': filtro_privilegios,
        'filtro_prestamos': filtro_prestamos,
        'total_usuarios': len(usuarios_data),
    }
    return render(request, 'core/gestionar_usuarios.html', context)




def cambiar_permiso_admin_view(request, codigo_usuario):
    if not es_admin_activo(request):
        return redirect('inicio')

    correo_actual = request.session.get('correo_usuario')
    usuario_actual = Usuario.objects.filter(correo=correo_actual).first()

    if usuario_actual and str(usuario_actual.codigo) == str(codigo_usuario):
        messages.error(request,'No puedes revocarte tus propios permisos de administrador.')
        return redirect('gestionar_usuarios')

    usuario = get_object_or_404(Usuario, codigo=codigo_usuario)
    admin_existente = Admin.objects.filter(codigo=usuario).first()

    if admin_existente is None:
        Admin.objects.create(codigo=usuario, activo=True)
        messages.success(request, f"{usuario.nombre} ahora es administrador.")

    elif admin_existente.activo:
        tiene_solicitudes = Solicitudprestamo.objects.filter(codigo_a=admin_existente).exists()

        tiene_devoluciones = Devolucion.objects.filter(codigo=admin_existente).exists()

        if tiene_solicitudes or tiene_devoluciones:
            admin_existente.activo = False
            admin_existente.save(update_fields=['activo'])

            messages.success(request, f"Se revocaron los permisos de administrador a " f"{usuario.nombre}. Su historial se conservó.")
        else:
            try:
                admin_existente.delete()
                messages.success(request, f"Se revocaron los permisos de administrador a " f"{usuario.nombre}.")
            except IntegrityError:
                # Si otra relación impide eliminarlo, se conserva el registro.
                admin_existente.activo = False
                admin_existente.save(update_fields=['activo'])
                messages.success(request, f"Se revocaron los permisos de administrador a " f"{usuario.nombre}. Su registro se conservó " f"para proteger el historial.")

    else:
        admin_existente.activo = True
        admin_existente.save(update_fields=['activo'])

        messages.success(request,f"{usuario.nombre} ahora es administrador.")

    return redirect('gestionar_usuarios')



def cambiar_estado_usuario_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')
        
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
    if not es_admin_activo(request):
        return redirect('inicio')
    
    # Préstamos que aún no tienen un registro de devolución asociado
    prestamos_activos = Prestamo.objects.filter(devolucion__isnull=True)

    context = {'prestamos': prestamos_activos}
    return render(request, 'core/procesar_devoluciones.html', context)






def registrar_devolucion_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')
    prestamo = get_object_or_404(Prestamo, idprestamo=pk)

    if request.method == 'POST':
        observaciones = (request.POST.get('observaciones') or '').strip()
        libro_perdido = request.POST.get('libro_perdido') == 'si'
        nivel_danio = request.POST.get('nivel_danio', '0')
        hoy = date.today()

        multas_danio = {
            '0': 0,
            '1': 1000,
            '2': 6000,
            '3': 12000,
        }

        if libro_perdido:
            multa = 30000
            observacion_estado = 'Libro reportado como perdido'
        else:
            multa_retraso = calcular_multa(prestamo.fechavencimiento, hoy)
            multa_danio = multas_danio.get(nivel_danio, 0)
            multa = multa_retraso + multa_danio

            if nivel_danio in ('1', '2', '3'):
                observacion_estado = f'Daño nivel {nivel_danio}'
            else:
                observacion_estado = ''

        if observacion_estado:
            observaciones = (
                f'{observaciones} - {observacion_estado}'
                if observaciones
                else observacion_estado
            )

        if not observaciones:
            observaciones = 'Devolución normal sin novedad'

        correo_admin = request.session.get('correo_usuario')
        admin_obj = Admin.objects.filter(codigo__correo=correo_admin).first()

        if not admin_obj:
            admin_obj = Admin.objects.first()

        if not admin_obj:
            messages.error(request,'No se encontró un administrador para registrar la devolución.')
            return redirect('procesar_devoluciones')

        ids_existentes = Devolucion.objects.values_list('iddevolucion',flat=True)
        numeros_usados = []

        for id_existente in ids_existentes:
            coincidencia = re.fullmatch(r'DEV(\d+)', id_existente)

            if coincidencia:
                numeros_usados.append(int(coincidencia.group(1)))

        siguiente_numero = max(numeros_usados, default=0) + 1
        id_devolucion = f'DEV{siguiente_numero:03d}'

        while Devolucion.objects.filter(iddevolucion=id_devolucion).exists():
            siguiente_numero += 1
            id_devolucion = f'DEV{siguiente_numero:03d}'


        if libro_perdido:
            observaciones = (
                f"{observaciones} - Libro reportado como perdido"
                if observaciones
                else 'Libro reportado como perdido'
            )
        Devolucion.objects.create(iddevolucion=id_devolucion,idprestamo=prestamo,codigo=admin_obj,fechadevolucion=hoy,observaciones=observaciones,multa=multa,pagado=False)

        if multa > 0:
            cliente = prestamo.idsolicitud.codigo_c
            cliente.estado = 'bloqueado'
            cliente.save(update_fields=['estado'])
        ejemplar = prestamo.codigobarras

        if libro_perdido:
            ejemplar.estado = 'perdido'
        else:
            ejemplar.estado = 'disponible'
        ejemplar.save()

        messages.success(request,f'¡Devolución registrada correctamente! 'f'Cliente: {prestamo.idsolicitud.codigo_c.codigo.nombre}. 'f'ID del préstamo: {prestamo.idprestamo}. 'f'Multa calculada: ${multa:,.0f} COP.')
        return redirect('procesar_devoluciones')
    return render(request,'core/registrar_devolucion.html',{'prestamo': prestamo})









def registrar_autor_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')

    libros = Libro.objects.all().order_by('titulo')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        libros_seleccionados = request.POST.getlist('libros')

        if not nombre:
            return render(request, 'core/form_autor.html', {'error': 'El nombre del autor es obligatorio.','libros': libros})

        if len(nombre) > 50:
            return render(request,'core/form_autor.html',
                {
                    'error': 'El nombre del autor no puede superar los 50 caracteres.',
                    'libros': libros
                }
            )

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
    if not es_admin_activo(request):
        return redirect('inicio')
    
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
    if not es_admin_activo(request):
        return redirect('inicio')

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



def gestionar_autores_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')
    autores = Autor.objects.all().order_by('nombre')

    for autor in autores:
        autor.tiene_libros = Escribe.objects.filter(idautor=autor).exists()
    return render(request,'core/gestionar_autores.html',{'autores': autores})




def editar_autor_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')

    if request.method != 'POST':
        return redirect('gestionar_autores')
    autor = get_object_or_404(Autor, pk=pk)
    nombre = request.POST.get('nombre', '').strip()

    if not nombre:
        messages.error(request, 'El nombre del autor no puede estar vacío.')
        return redirect('gestionar_autores')

    if len(nombre) > 50:
        messages.error(request,'El nombre del autor no puede superar los 50 caracteres.')
        return redirect('gestionar_autores')

    autor.nombre = nombre
    autor.save(update_fields=['nombre'])
    messages.success(request,f'El nombre del autor se actualizó a "{nombre}".')
    return redirect('gestionar_autores')


def eliminar_autor_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')

    if request.method != 'POST':
        return redirect('gestionar_autores')

    autor = get_object_or_404(Autor, pk=pk)
    relaciones = Escribe.objects.filter(idautor=autor)

    # Si tiene libros asociados
    if relaciones.exists():
        desvincular = request.POST.get('desvincular')

        if desvincular != 'si':
            messages.info(request,'El autor tiene libros asociados. ''Debes confirmar si deseas desvincularlos y eliminarlo.')
            return redirect('gestionar_autores')

    nombre_autor = autor.nombre

    try:
        with transaction.atomic():
            # Eliminar las asociaciones
            relaciones.delete()
            autor.delete()
        messages.success(request,f"El autor '{nombre_autor}' fue eliminado correctamente.")
    except Exception:
        messages.error(request,'No se pudo eliminar el autor. ''Verifica sus relaciones con otros registros.')

    return redirect('gestionar_autores')




def historial_prestamos_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')

    historial = Prestamo.objects.filter(devolucion__isnull=False).select_related('idsolicitud__codigo_c__codigo','idsolicitud__isbn','codigobarras','devolucion')

    usuario_seleccionado = request.GET.get('usuario', '')
    estado_pago = request.GET.get('estado_pago', 'todos')

    if usuario_seleccionado:
        historial = historial.filter(idsolicitud__codigo_c__pk=usuario_seleccionado)

    if estado_pago == 'pendiente':
        historial = historial.filter(devolucion__multa__gt=0,devolucion__pagado=False)
    elif estado_pago == 'pagado':
        historial = historial.filter(devolucion__multa__gt=0,devolucion__pagado=True)
    elif estado_pago == 'sin_multa':
        historial = historial.filter(devolucion__multa=0)
    historial = historial.order_by(models.Case(models.When(devolucion__multa__gt=0,devolucion__pagado=False,then=models.Value(1)),models.When(devolucion__multa__gt=0,devolucion__pagado=True,then=models.Value(2)),default=models.Value(3),output_field=models.IntegerField()),'-devolucion__fechadevolucion')
    usuarios = Cliente.objects.filter(solicitudprestamo__prestamo__devolucion__isnull=False).select_related('codigo').distinct().order_by('codigo__nombre')

    context = {
        'historial': historial,
        'usuarios': usuarios,
        'usuario_seleccionado': usuario_seleccionado,
        'estado_pago': estado_pago,
    }
    return render(request,'core/historial_prestamos.html',context)





def dashboard_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')

    total_libros = Libro.objects.count()
    total_prestamos = Prestamo.objects.count()
    total_solicitudes = Solicitudprestamo.objects.count()
    prestamos_activos = Prestamo.objects.filter(devolucion__isnull=True).count()

    
    # Top 5 Libros
    top_libros = Libro.objects.annotate(cantidad=Count('ejemplar__prestamo')).filter(cantidad__gt=0).order_by('-cantidad')[:5]
    data_top_libros = {'labels': [l.titulo for l in top_libros],'data': [l.cantidad for l in top_libros],'tipoGrafico': 'bar'}


    # Deudas
    estudiantes_deudas = Cliente.objects.filter(rol__iexact='estudiante', solicitudprestamo__prestamo__devolucion__multa__gt=0).annotate(deuda=Sum('solicitudprestamo__prestamo__devolucion__multa')).order_by('-deuda')
    data_deudas = {
        'labels': [e.codigo.nombre for e in estudiantes_deudas],
        'data': [float(e.deuda) for e in estudiantes_deudas],
        'tipoGrafico': 'bar'
    }


    # Inventario Físico
    ejemplares = Ejemplar.objects.values('estado').annotate(cantidad=Count('estado')).order_by('-cantidad')
    data_inventario = {
        'labels': [e['estado'].capitalize() for e in ejemplares],
        'data': [e['cantidad'] for e in ejemplares],
        'tipoGrafico': 'doughnut'
    }


    # Historial en el tiempo
    historial = Prestamo.objects.annotate(anio=ExtractYear('fechaprestamo'), mes=ExtractMonth('fechaprestamo')).values('anio', 'mes').annotate(cantidad=Count('idprestamo')).order_by('anio', 'mes')
    data_historial = {
        'labels': [f"{h['mes']:02d}/{h['anio']}" for h in historial],
        'data': [h['cantidad'] for h in historial],
        'tipoGrafico': 'line'
    }

    
    # Préstamos vencidos y vigentes
    hoy = timezone.localdate()
    prestamos_vencidos = Prestamo.objects.filter(devolucion__isnull=True,fechavencimiento__lt=hoy).count()
    prestamos_vigentes = Prestamo.objects.filter(devolucion__isnull=True,fechavencimiento__gte=hoy).count()
    data_estado_prestamos = {
        'labels': ['Vigentes', 'Vencidos'],
        'data': [prestamos_vigentes, prestamos_vencidos],
        'tipoGrafico': 'doughnut'
    }

    # Detalle de préstamos que aún no han sido devueltos
    prestamos_pendientes = Prestamo.objects.filter(devolucion__isnull=True).select_related('idsolicitud__codigo_c__codigo','codigobarras__isbn').order_by('fechavencimiento')
    detalle_prestamos = []

    for prestamo in prestamos_pendientes:
        detalle_prestamos.append({
            'id': prestamo.idprestamo,
            'usuario': prestamo.idsolicitud.codigo_c.codigo.nombre,
            'codigo_usuario': prestamo.idsolicitud.codigo_c.codigo.codigo,
            'libro': prestamo.codigobarras.isbn.titulo,
            'ejemplar': prestamo.codigobarras.codigobarras,
            'fecha_prestamo': prestamo.fechaprestamo,
            'fecha_vencimiento': prestamo.fechavencimiento,
            'estado': ('Vencido' if prestamo.fechavencimiento < hoy else 'Vigente')
        })


    # Top 5 usuarios con más préstamos
    top_usuarios = Cliente.objects.annotate(cantidad=Count('solicitudprestamo__prestamo__idprestamo', distinct=True)).filter(cantidad__gt=0).order_by('-cantidad', 'codigo')[:5]
    data_top_usuarios = {
        'labels': [u.codigo.nombre for u in top_usuarios],
        'data': [u.cantidad for u in top_usuarios],
        'tipoGrafico': 'bar'
    }


    datos_graficos = {
        'top_libros': data_top_libros,
        'deudas': data_deudas,
        'inventario': data_inventario,
        'historial': data_historial,
        'estado_prestamos': data_estado_prestamos,
        'top_usuarios': data_top_usuarios
    }

    # --- 3. Enviamos TODO al contexto ---
    context = {
        'total_libros': total_libros,
        'total_prestamos': total_prestamos,
        'total_solicitudes': total_solicitudes,
        'prestamos_activos': prestamos_activos,
        'datos_json': json.dumps(datos_graficos, cls=DjangoJSONEncoder),
        'detalle_prestamos': detalle_prestamos
    }
    return render(request, 'core/dashboard.html', context)




def mis_multas_view(request):
    if not request.session.get('rol'):
        return redirect('login')

    correo_usuario = request.session.get('correo_usuario')

    multas = Devolucion.objects.filter(idprestamo__idsolicitud__codigo_c__codigo__correo=correo_usuario,multa__gt=0).select_related('idprestamo__idsolicitud__isbn','idprestamo').order_by('pagado','-fechadevolucion')
    multas_pendientes = multas.filter(pagado=False)
    context = {
        'multas': multas,
        'total_multas': multas_pendientes.count(),
        'valor_total': sum(multa.multa for multa in multas_pendientes),
    }
    return render(request, 'core/mis_multas.html', context)







def gestionar_multas_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')
    multas = Devolucion.objects.filter(multa__gt=0).select_related('idprestamo__idsolicitud__codigo_c__codigo','idprestamo__idsolicitud__isbn').order_by('pagado', '-fechadevolucion')
    multas_por_usuario = {}

    for multa in multas:
        cliente = multa.idprestamo.idsolicitud.codigo_c
        codigo_cliente = cliente.pk

        if codigo_cliente not in multas_por_usuario:
            multas_por_usuario[codigo_cliente] = {
                'cliente': cliente,
                'total': 0
            }

        if not multa.pagado:
            multas_por_usuario[codigo_cliente]['total'] += multa.multa

    for datos in multas_por_usuario.values():
        if datos['total'] > 0:
            datos['estado_multas'] = 'bloqueado'
        else:
            datos['estado_multas'] = 'activo'

    context = {
        'multas': multas,
        'total_multas': multas.filter(pagado=False).count(),
        'valor_total': sum(multa.multa for multa in multas if not multa.pagado),
        'multas_por_usuario': multas_por_usuario.values(),
    }
    return render(request,'core/gestionar_multas.html',context)



def reactivar_cliente_view(request, pk):
    if not es_admin_activo(request):
        return redirect('inicio')

    if request.method != 'POST':
        return redirect('gestionar_multas')
    
    cliente = get_object_or_404(Cliente, pk=pk)
    if cliente.estado == 'activo':
        messages.info(request,f'El usuario {cliente.codigo.nombre} ya está activo.')
        return redirect('gestionar_multas')
    confirmacion = request.POST.get('confirmar_pago')

    if confirmacion != 'si':
        messages.error(request,'Debes confirmar que el usuario resolvió sus multas.')
        return redirect('gestionar_multas')
    cliente.estado = 'activo'
    cliente.save(update_fields=['estado'])
    messages.success(request,f'El usuario {cliente.codigo.nombre} fue reactivado correctamente.')

    return redirect('gestionar_multas')



def marcar_multa_pagada_view(request, iddevolucion):
    if not es_admin_activo(request):
        return redirect('inicio')

    if request.method != 'POST':
        return redirect('gestionar_multas')
    multa = get_object_or_404(Devolucion,iddevolucion=iddevolucion)
    multa.pagado = True
    multa.save(update_fields=['pagado'])
    messages.success(request,'La multa se marcó como pagada correctamente.')

    return redirect('gestionar_multas')



def mi_historial_prestamos_view(request):
    if request.session.get('rol') not in ['estudiante', 'docente']:
        return redirect('inicio')

    correo_usuario = request.session.get('correo_usuario')
    historial = Prestamo.objects.filter(devolucion__isnull=False,idsolicitud__codigo_c__codigo__correo=correo_usuario).select_related('idsolicitud__codigo_c__codigo','idsolicitud__isbn','codigobarras','devolucion').order_by('-devolucion__fechadevolucion')
    return render(request,'core/mi_historial_prestamos.html',{'historial': historial})



def sugerencias_libros_view(request):
    q = request.GET.get('q', '').strip()

    # Si no hay texto suficiente, no mostramos sugerencias
    if len(q) < 2:
        return JsonResponse([], safe=False)

    # Consulta base con la cantidad de ejemplares disponibles
    libros = Libro.objects.annotate(disponibles_count=Count('ejemplar',filter=Q(ejemplar__estado__iexact='disponible')))

    # Aplicamos los mismos criterios de búsqueda del catálogo
    palabras = q.split()
    filtros_palabras = []

    for palabra in palabras:
        filtro = (Q(titulo__icontains=palabra) | Q(isbn__icontains=palabra) | Q(escribe__idautor__nombre__icontains=palabra) | Q(pertenece__idcategoria__nombre__icontains=palabra))
        filtros_palabras.append(filtro)
    libros = libros.filter(reduce(operator.and_, filtros_palabras)).distinct().order_by('-disponibles_count', 'titulo')[:5]


    sugerencias = []

    # Sugerencias de categorías: primero
    categorias_encontradas = Categoria.objects.filter(nombre__icontains=q).order_by('nombre')[:5]

    for categoria in categorias_encontradas:
        sugerencias.append({'tipo': 'categoria','id': categoria.idcategoria, 'nombre': categoria.nombre})
    # Sugerencias de autores: después de las categorías
    autores_encontrados = Autor.objects.filter(nombre__icontains=q).order_by('nombre')[:5]

    for autor in autores_encontrados:
        sugerencias.append({'tipo': 'autor', 'id': autor.idautor, 'nombre': autor.nombre})

    # Sugerencias de libros: después
    for libro in libros:
        categorias = Pertenece.objects.filter(isbn=libro).select_related('idcategoria')
        nombres_categorias = [relacion.idcategoria.nombre for relacion in categorias]
        autores = Escribe.objects.filter(isbn=libro).select_related('idautor')
        nombres_autores = [relacion.idautor.nombre for relacion in autores]

        sugerencias.append({
            'tipo': 'libro',
            'isbn': libro.isbn,
            'titulo': libro.titulo,
            'autores': nombres_autores,
            'categorias': nombres_categorias,
            'disponibles': libro.disponibles_count
        })
    return JsonResponse(sugerencias[:5], safe=False)



def isbn_valido(isbn):
    # Quitar guiones y espacios
    isbn = isbn.replace('-', '').replace(' ', '').upper()

    # ISBN-10
    if len(isbn) == 10:
        if not isbn[:9].isdigit():
            return False

        if not (isbn[9].isdigit() or isbn[9] == 'X'):
            return False
        digitos = [int(c) for c in isbn[:9]]
        digitos.append(10 if isbn[9] == 'X' else int(isbn[9]))

        suma = sum(
            digito * (10 - i)
            for i, digito in enumerate(digitos)
        )
        return suma % 11 == 0

    # ISBN-13
    if len(isbn) == 13:
        if not isbn.isdigit():
            return False

        suma = sum(
            int(digito) * (1 if i % 2 == 0 else 3)
            for i, digito in enumerate(isbn[:12])
        )
        digito_control = (10 - suma % 10) % 10
        return digito_control == int(isbn[12])
    return False



def registrar_editorial_view(request):
    if not es_admin_activo(request):
        return redirect('inicio')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()

        # Validar nombre
        if not nombre:
            return render(request,'core/form_editorial.html',{'error': 'El nombre de la editorial es obligatorio.'})

        if len(nombre) > 50:
            return render(request,'core/form_editorial.html',{'error': 'El nombre no puede superar los 50 caracteres.'})

        # Generar el siguiente identificador: ED001, ED002...
        ids_existentes = Editorial.objects.values_list('ideditorial', flat=True)
        numeros_usados = []

        for ideditorial in ids_existentes:
            coincidencia = re.fullmatch(r'ED(\d+)', ideditorial)

            if coincidencia:
                numeros_usados.append(int(coincidencia.group(1)))

        siguiente_numero = max(numeros_usados, default=0) + 1
        nuevo_id = f'ED{siguiente_numero:03d}'

        while Editorial.objects.filter(ideditorial=nuevo_id).exists():
            siguiente_numero += 1
            nuevo_id = f'ED{siguiente_numero:03d}'

        Editorial.objects.create(ideditorial=nuevo_id,nombre=nombre)
        messages.success(request,f'Editorial registrada correctamente. ID: {nuevo_id}. Nombre: {nombre}.')
        return redirect('registrar_editorial')
    return render(request, 'core/form_editorial.html')