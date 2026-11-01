from django.db import models


class Distribuidor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo_barras = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField()
    stock = models.IntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    distribuidor = models.ForeignKey(Distribuidor, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def bajo_minimo(self):
        return self.stock <= self.stock_minimo

    def __str__(self):
        return self.nombre


class Lote(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    cantidad = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField()
    fecha_entrada = models.DateField(auto_now_add=True)


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)

    @property
    def saldo(self):
        fiado = sum(v.total for v in self.ventas.filter(medio_pago='FIADO'))
        abonos = sum(a.valor for a in self.abonos.all())
        return fiado - abonos

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    MEDIOS = [('EFECTIVO', 'Efectivo'), ('TRANSFERENCIA', 'Transferencia'), ('FIADO', 'Fiado')]
    fecha = models.DateTimeField(auto_now_add=True)
    medio_pago = models.CharField(max_length=15, choices=MEDIOS)
    total = models.PositiveIntegerField(default=0)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.PROTECT, related_name='ventas')
    cajero = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Abono(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='abonos')
    valor = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)


class Alerta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    atendida = models.BooleanField(default=False)
