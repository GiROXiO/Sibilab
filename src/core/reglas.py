from .models import Cliente, Ejemplar


def validar_solicitud_prestamo(codigo_usuario, codigo_barras):
    try:
        usuario = Cliente.objects.get(codigo=codigo_usuario)
        ejemplar = Ejemplar.objects.get(codigobarras=codigo_barras)
    except (Cliente.DoesNotExist, Ejemplar.DoesNotExist):
        return False

    return (usuario.estado.upper() == "ACTIVO" and ejemplar.estado.upper() == "DISPONIBLE")

def calcular_multa(fecha_vencimiento, fecha_actual):
    pass