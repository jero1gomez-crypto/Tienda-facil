from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Cliente, Alerta, Venta
from . import services


def es_admin(user):
    if not user.is_staff:
        raise PermissionDenied('No tiene permisos')  # RNF-03: HTTP 403
    return True


@login_required
def inicio(request):
    hoy = date.today()
    ctx = {
        'ventas_hoy': Venta.objects.filter(fecha__date=hoy).count(),
        'alertas': Alerta.objects.filter(atendida=False).select_related('producto')[:8],
        'vencen': services.proximos_a_vencer(),
    }
    return render(request, 'pos/inicio.html', ctx)


@login_required
def nueva_venta(request):
    carrito = request.session.get('carrito', [])
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'agregar':
            codigo = request.POST.get('codigo', '').strip()
            cant = int(request.POST.get('cantidad') or 1)
            if Producto.objects.filter(codigo_barras=codigo).exists():
                carrito.append([codigo, cant])
            else:
                messages.error(request, f'Producto no encontrado: {codigo}')
        elif accion == 'vaciar':
            carrito = []
        elif accion == 'confirmar':
            medio = request.POST.get('medio_pago')
            cid = request.POST.get('cliente')
            cliente = Cliente.objects.filter(pk=cid).first() if cid else None
            try:
                v = services.registrar_venta(carrito, medio, cliente, request.user)
                messages.success(request, f'Venta #{v.id} guardada por ${v.total:,}'.replace(',', '.'))
                carrito = []
            except services.ErrorVenta as e:
                messages.error(request, str(e))
        request.session['carrito'] = carrito
        return redirect('nueva_venta')
    lineas, total = [], 0
    for codigo, cant in carrito:
        p = Producto.objects.get(codigo_barras=codigo)
        lineas.append({'p': p, 'cant': cant, 'sub': p.precio * cant})
        total += p.precio * cant
    return render(request, 'pos/venta.html', {'lineas': lineas, 'total': total, 'clientes': Cliente.objects.all()})


@login_required
def inventario(request):
    return render(request, 'pos/inventario.html', {'productos': Producto.objects.select_related('distribuidor').order_by('nombre')})


@login_required
def entrada(request):
    if request.method == 'POST':
        p = get_object_or_404(Producto, pk=request.POST['producto'])
        services.registrar_entrada(p, int(request.POST['cantidad']), request.POST['vence'])
        messages.success(request, f'Entrada registrada. {p.nombre}: {p.stock} unidades')
        return redirect('inventario')
    return render(request, 'pos/entrada.html', {'productos': Producto.objects.order_by('nombre')})


@login_required
def fiado(request):
    if request.method == 'POST':
        c = get_object_or_404(Cliente, pk=request.POST['cliente'])
        services.registrar_abono(c, int(request.POST['valor']))
        messages.success(request, f'Abono registrado a {c.nombre}')
        return redirect('fiado')
    return render(request, 'pos/fiado.html', {'clientes': Cliente.objects.order_by('nombre')})


@login_required
@user_passes_test(es_admin)
def cierre(request):
    dia = request.GET.get('dia') or date.today().isoformat()
    return render(request, 'pos/cierre.html', {'r': services.cierre_de_caja(date.fromisoformat(dia)), 'dia': dia})


@login_required
@user_passes_test(es_admin)
def pedido(request):
    return render(request, 'pos/pedido.html', {'grupos': services.pedido_sugerido()})
