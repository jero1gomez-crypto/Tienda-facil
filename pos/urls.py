from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='pos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.inicio, name='inicio'),
    path('venta/', views.nueva_venta, name='nueva_venta'),
    path('inventario/', views.inventario, name='inventario'),
    path('entrada/', views.entrada, name='entrada'),
    path('fiado/', views.fiado, name='fiado'),
    path('reportes/cierre/', views.cierre, name='cierre'),
    path('reportes/pedido/', views.pedido, name='pedido'),
]
