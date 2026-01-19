from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/', views.pago, name='pago'),
    path('guardar-pedido/', views.guardar_pedido, name='guardar_pedido'),
    path('ticket/<int:pedido_id>/', views.ticket, name='ticket'),
    path('historial/', views.historial_pedidos, name='historial'),
    path('ticket/pdf/<int:pedido_id>/', views.ticket_pdf, name='ticket_pdf'),
    path('calificar/', views.guardar_calificacion, name='guardar_calificacion'),
    path('promedio-calificaciones/', views.promedio_calificaciones, name='promedio_calificaciones'),
    path('calificar/<int:pedido_id>/', views.calificar, name='calificar'),
    path('mis-pedidos/', views.buscar_pedidos, name='buscar_pedidos'),
    path('login-email/', views.login_email, name='login_email'),
    path('logout-email/', views.logout_email, name='logout_email'),
    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('cambiar-estado/<int:pedido_id>/', views.cambiar_estado, name='cambiar_estado'),
    path('metricas/', views.metricas, name='metricas'),
]
