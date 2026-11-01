# TiendaFácil – Sistema POS del Minimercado La Esquina

Sistema de punto de venta para una tienda de barrio: registra ventas con lector de código de barras, controla el inventario con alertas de stock mínimo y vencimientos, sugiere pedidos por distribuidor, lleva el fiado de cada cliente y genera el cierre de caja diario.

**Equipo:** Juan Esteban López Pino · Anderson Jerónimo Gómez Duque
**Versión actual:** 1.2.1 (ver [CHANGELOG](CHANGELOG.md))

## Tecnologías
Python 3.12 · Django 5.0 · PostgreSQL 16 · Bootstrap 5 · Docker · pytest · Locust

## Funcionalidades
| Requisito | Funcionalidad | Ruta |
| --- | --- | --- |
| RF-01 | Registrar venta con código de barras | `/venta/` |
| RF-02 | Alerta de stock mínimo | `/` (inicio) |
| RF-03 | Pedido sugerido por distribuidor | `/reportes/pedido/` |
| RF-04 | Entrada de mercancía con vencimiento | `/entrada/` |
| RF-05 | Productos que vencen en 7 días | `/` (inicio) |
| RF-06 / RF-07 | Venta fiada, abonos y saldo | `/fiado/` |
| RF-08 | Cierre de caja por medio de pago | `/reportes/cierre/` |

## Instalación con Docker (producción)
```bash
git clone https://github.com/<usuario>/tiendafacil.git && cd tiendafacil
cp .env.example .env            # completar SECRET_KEY y POSTGRES_PASSWORD
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py datos_demo   # opcional
docker compose exec web pytest
```
Abrir `http://<IP del servidor>:8000` desde cada caja.

## Ejecución local sin Docker (desarrollo)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py datos_demo
python manage.py runserver
```
Usuarios de demostración: `dueno` (administrador) y `cajero`, clave `Clave123*`.

## Pruebas
- Unitarias y de aceptación: `pytest` (9 pruebas).
- Carga (CP-05): `locust -f locustfile.py --host http://localhost:8000 -u 3 -r 3 -t 5m --headless`

## Ramas
`main` (producción) · `develop` (pruebas) · `feature/*` · `hotfix/*`
