from datetime import date, timedelta
import pytest
from django.contrib.auth.models import User
from pos.models import Producto, Cliente, Alerta, Distribuidor
from pos import services

pytestmark = pytest.mark.django_db


@pytest.fixture
def productos():
    d = Distribuidor.objects.create(nombre='Distribuidora A')
    return {
        'arroz': Producto.objects.create(codigo_barras='7701', nombre='Arroz 500 g', precio=3000, stock=50, distribuidor=d),
        'aceite': Producto.objects.create(codigo_barras='7702', nombre='Aceite 1 L', precio=12000, stock=20, distribuidor=d),
        'leche': Producto.objects.create(codigo_barras='7703', nombre='Leche 1 L', precio=4500, stock=6, stock_minimo=5, distribuidor=d),
    }


def test_cp01_venta_total_y_stock(productos):  # RF-01
    v = services.registrar_venta([('7701', 2), ('7702', 1)], 'EFECTIVO')
    assert v.total == 18000
    productos['arroz'].refresh_from_db(); productos['aceite'].refresh_from_db()
    assert productos['arroz'].stock == 48 and productos['aceite'].stock == 19


def test_cp02_alerta_stock_minimo(productos):  # RF-02
    services.registrar_venta([('7703', 1)], 'EFECTIVO')
    assert Alerta.objects.filter(mensaje='Stock bajo: Leche 1 L').exists()


def test_cp03_fiado_y_abono(productos):  # RF-06, RF-07
    p = Producto.objects.create(codigo_barras='9000', nombre='Mercado', precio=25000, stock=5)
    maria = Cliente.objects.create(nombre='María Pérez')
    services.registrar_venta([('9000', 1)], 'FIADO', cliente=maria)
    services.registrar_abono(maria, 10000)
    assert maria.saldo == 15000


def test_fiado_sin_cliente_falla(productos):
    with pytest.raises(services.ErrorVenta):
        services.registrar_venta([('7701', 1)], 'FIADO')


def test_cp04_cierre_de_caja():  # RF-08
    Producto.objects.create(codigo_barras='1', nombre='A', precio=300000, stock=5)
    Producto.objects.create(codigo_barras='2', nombre='B', precio=150000, stock=5)
    services.registrar_venta([('1', 1)], 'EFECTIVO')
    services.registrar_venta([('2', 1)], 'TRANSFERENCIA')
    r = services.cierre_de_caja()
    assert (r['EFECTIVO'], r['TRANSFERENCIA'], r['TOTAL']) == (300000, 150000, 450000)


def test_rf04_entrada_con_vencimiento(productos):
    p = Producto.objects.create(codigo_barras='8000', nombre='Yogur', precio=2500, stock=10)
    services.registrar_entrada(p, 24, date(2026, 11, 30))
    assert p.stock == 34 and p.lotes.first().fecha_vencimiento == date(2026, 11, 30)


def test_rf05_proximos_a_vencer(productos):
    hoy = date(2026, 11, 1)
    p = productos['leche']
    services.registrar_entrada(p, 5, hoy + timedelta(days=5))
    services.registrar_entrada(p, 5, hoy + timedelta(days=20))
    assert services.proximos_a_vencer(7, hoy).count() == 1


def test_rf03_pedido_sugerido(productos):
    services.registrar_venta([('7703', 1)], 'EFECTIVO')
    assert [p.nombre for p in services.pedido_sugerido()['Distribuidora A']] == ['Leche 1 L']


def test_m03_cajero_no_ve_reportes(client):  # RNF-03 / M-03
    User.objects.create_user('cajero', password='Clave123*')
    client.login(username='cajero', password='Clave123*')
    rechazados = sum(client.get(u).status_code == 403 for u in ['/reportes/cierre/', '/reportes/pedido/'] * 10)
    assert rechazados == 20
