"""Carga datos de demostración del Minimercado La Esquina."""
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pos.models import Distribuidor, Producto, Cliente
from pos import services


class Command(BaseCommand):
    help = 'Crea productos, clientes, usuarios y ventas de ejemplo'

    def handle(self, *args, **kw):
        if Producto.objects.exists():
            self.stdout.write('Ya hay datos; no se cargó nada.')
            return
        a = Distribuidor.objects.create(nombre='Distribuidora El Granero', telefono='3001234567')
        b = Distribuidor.objects.create(nombre='Lácteos del Valle', telefono='3109876543')
        c = Distribuidor.objects.create(nombre='Bebidas Andinas', telefono='3155550000')
        datos = [('7702001', 'Arroz Diana 500 g', 3000, 40, 10, a), ('7702002', 'Aceite Premier 1 L', 12000, 15, 5, a),
                 ('7702003', 'Panela 500 g', 2800, 8, 6, a), ('7702004', 'Café Sello Rojo 250 g', 9500, 12, 4, a),
                 ('7703001', 'Leche entera 1 L', 4500, 6, 5, b), ('7703002', 'Yogur fresa 200 g', 2500, 20, 6, b),
                 ('7703003', 'Queso campesino 250 g', 7800, 4, 4, b), ('7704001', 'Gaseosa 1,5 L', 5500, 24, 8, c),
                 ('7704002', 'Agua 600 ml', 1800, 30, 10, c), ('7705001', 'Jabón Rey', 2900, 18, 5, None)]
        for cod, n, pr, st, mn, d in datos:
            Producto.objects.create(codigo_barras=cod, nombre=n, precio=pr, stock=st, stock_minimo=mn, distribuidor=d)
        services.registrar_entrada(Producto.objects.get(codigo_barras='7703002'), 12, date.today() + timedelta(days=5))
        services.registrar_entrada(Producto.objects.get(codigo_barras='7703003'), 6, date.today() + timedelta(days=3))
        maria = Cliente.objects.create(nombre='María Pérez', telefono='3201112233')
        Cliente.objects.create(nombre='Jorge Ramírez', telefono='3114445566')
        Cliente.objects.create(nombre='Luz Marina Ortiz', telefono='3127778899')
        dueno = User.objects.create_user('dueno', password='Clave123*', first_name='Don Hernando', is_staff=True)
        cajero = User.objects.create_user('cajero', password='Clave123*', first_name='Carlos')
        services.registrar_venta([('7702001', 2), ('7702002', 1)], 'EFECTIVO', cajero=cajero)
        services.registrar_venta([('7704001', 2), ('7705001', 1)], 'TRANSFERENCIA', cajero=cajero)
        services.registrar_venta([('7702004', 1), ('7703001', 2)], 'FIADO', cliente=maria, cajero=cajero)
        services.registrar_abono(maria, 10000)
        self.stdout.write(self.style.SUCCESS('Datos de demostración cargados (usuarios: dueno / cajero, clave Clave123*)'))
