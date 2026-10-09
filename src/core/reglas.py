from .models import Cliente, Ejemplar


def validar_solicitud_prestamo(codigo_usuario, codigo_barras):
    try:
        usuario = Cliente.objects.get(codigo=codigo_usuario)
        ejemplar = Ejemplar.objects.get(codigobarras=codigo_barras)
    except (Cliente.DoesNotExist, Ejemplar.DoesNotExist):
        return False

    return (usuario.estado.upper() == "ACTIVO" and ejemplar.estado.upper() == "DISPONIBLE")

def calcular_multa(fecha_vencimiento, fecha_actual):
    TARIFA_MULTA_DIARIA = 2000
    dias_retraso = max(0, (fecha_actual - fecha_vencimiento).days)
    return dias_retraso * TARIFA_MULTA_DIARIA