"""Reglas de negocio de TiendaFácil (RF-01 a RF-08)."""
from datetime import date, timedelta
from collections import defaultdict
from django.db import transaction
from django.db.models import Sum
from .models import Producto, Venta, DetalleVenta, Alerta, Lote, Abono


class ErrorVenta(Exception):
    pass


def revisar_stock(producto):
    """RF-02: crea una alerta cuando el producto llega a su stock mínimo."""
    if producto.stock <= producto.stock_minimo:
        return Alerta.objects.create(producto=producto, mensaje=f'Stock bajo: {producto.nombre}')
    return None


@transaction.atomic
def registrar_venta(items, medio_pago, cliente=None, cajero=None):
    """RF-01 / RF-06: items = [(codigo_barras, cantidad), ...]."""
    if not items:
        raise ErrorVenta('La venta no tiene productos')
    if medio_pago == 'FIADO' and cliente is None:
        raise ErrorVenta('Una venta fiada necesita un cliente')
    venta = Venta.objects.create(medio_pago=medio_pago, cliente=cliente, cajero=cajero)
    total = 0
    for codigo, cantidad in items:
        try:
            p = Producto.objects.select_for_update().get(codigo_barras=codigo)
        except Producto.DoesNotExist:
            raise ErrorVenta(f'Producto no encontrado: {codigo}')
        DetalleVenta.objects.create(venta=venta, producto=p, cantidad=cantidad, precio_unitario=p.precio)
        p.stock -= cantidad
        p.save()
        revisar_stock(p)
        total += cantidad * p.precio
    venta.total = total
    venta.save()
    return venta


def registrar_entrada(producto, cantidad, fecha_vencimiento):
    """RF-04: entrada de mercancía con fecha de vencimiento."""
    Lote.objects.create(producto=producto, cantidad=cantidad, fecha_vencimiento=fecha_vencimiento)
    producto.stock += cantidad
    producto.save()
    return producto


def proximos_a_vencer(dias=7, hoy=None):
    """RF-05: lotes que vencen en los próximos `dias` días."""
    hoy = hoy or date.today()
    return Lote.objects.filter(fecha_vencimiento__gte=hoy,
                               fecha_vencimiento__lte=hoy + timedelta(days=dias)).select_related('producto')


def pedido_sugerido():
    """RF-03: productos bajo su mínimo agrupados por distribuidor."""
    grupos = defaultdict(list)
    for p in Producto.objects.select_related('distribuidor').order_by('nombre'):
        if p.bajo_minimo:
            grupos[p.distribuidor.nombre if p.distribuidor else 'Sin distribuidor'].append(p)
    return dict(grupos)


def registrar_abono(cliente, valor):
    return Abono.objects.create(cliente=cliente, valor=valor)


def cierre_de_caja(dia=None):
    """RF-08: totales del día por medio de pago."""
    dia = dia or date.today()
    filas = Venta.objects.filter(fecha__date=dia).values('medio_pago').annotate(total=Sum('total'))
    resumen = {m: 0 for m, _ in Venta.MEDIOS}
    for f in filas:
        resumen[f['medio_pago']] = f['total']
    resumen['TOTAL'] = sum(resumen.values())
    return resumen
