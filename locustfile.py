"""CP-05 / M-02: 3 cajas confirmando ventas al mismo tiempo.
Uso: locust -f locustfile.py --host http://localhost:8000 -u 3 -r 3 -t 5m --headless
"""
import re
from locust import HttpUser, task, between


class Caja(HttpUser):
    wait_time = between(9, 11)

    def on_start(self):
        r = self.client.get('/login/')
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text).group(1)
        self.client.post('/login/', {'username': 'cajero', 'password': 'Clave123*', 'csrfmiddlewaretoken': token})

    def csrf(self):
        return self.client.cookies.get('csrftoken')

    @task
    def vender(self):
        for codigo in ['7702001', '7702002', '7704001', '7704002', '7705001']:
            self.client.post('/venta/', {'accion': 'agregar', 'codigo': codigo, 'cantidad': 1, 'csrfmiddlewaretoken': self.csrf()}, name='agregar')
        self.client.post('/venta/', {'accion': 'confirmar', 'medio_pago': 'EFECTIVO', 'csrfmiddlewaretoken': self.csrf()}, name='confirmar venta')
