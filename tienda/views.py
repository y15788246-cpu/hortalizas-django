from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Sum
import json
from django.db import transaction
import stripe
from django.conf import settings
from django.shortcuts import render, redirect

from .models import Pedido, DetallePedido, Producto, Calificacion
from .utils import render_to_pdf, enviar_ticket_por_correo

def index(request):
    promedio = Calificacion.objects.aggregate(avg=Avg('estrellas'))['avg']
    comentarios = Calificacion.objects.exclude(comentario='').order_by('-fecha')[:5]

    return render(request, 'tienda/index.html', {
        'promedio': round(promedio or 0, 1),
        'comentarios': comentarios
    })

def carrito(request):
    return render(request, 'tienda/carrito.html')

def pago(request):
    return render(request, 'tienda/pago.html')


def catalogo(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/catalogo.html', {
        'productos': productos
    })

@csrf_exempt
def guardar_pedido(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        with transaction.atomic():

            pedido = Pedido.objects.create(
                direccion=data['direccion'],
                metodo_pago=data['metodo_pago'],
                email=data['email'],
                total=0
            )

            total = 0

            for item in data['carrito']:
                producto = Producto.objects.select_for_update().get(id=item['id'])

                if producto.stock < item['cantidad']:
                    return JsonResponse({
                        'ok': False,
                        'error': f'Stock insuficiente para {producto.nombre}'
                    })

                subtotal = producto.precio * item['cantidad']

                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item['cantidad'],
                    subtotal=subtotal
                )

                # ✅ DESCONTAR STOCK REAL
                producto.stock -= item['cantidad']
                producto.save()

                total += subtotal

            pedido.total = total
            pedido.save()

            enviar_ticket_por_correo(
                pedido,
                DetallePedido.objects.filter(pedido=pedido),
                pedido.email
            )

            return JsonResponse({
                'ok': True,
                'pedido_id': pedido.id
            })

def ticket(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)

    return render(request, 'tienda/ticket.html', {
        'pedido': pedido,
        'detalles': detalles
    })



def ticket_pdf(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)

    context = {
        'pedido': pedido,
        'detalles': detalles
    }

    return render_to_pdf('tienda/ticket_pdf.html', context)

def historial_pedidos(request):
    pedidos = Pedido.objects.order_by('-fecha')

    return render(request, 'tienda/historial.html', {
        'pedidos': pedidos
    })

@csrf_exempt
def guardar_calificacion(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        estrellas = request.POST.get('estrellas')
        comentario = request.POST.get('comentario', '')

        pedido = Pedido.objects.get(id=pedido_id)

        Calificacion.objects.create(
            pedido=pedido,
            estrellas=estrellas,
            comentario=comentario
        )

        return JsonResponse({'status': 'ok'})
    
def promedio_calificaciones(request):
    promedio = Calificacion.objects.aggregate(avg=Avg('estrellas'))['avg']
    return JsonResponse({
        'promedio': round(promedio or 0, 1)
    })



def calificar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if Calificacion.objects.filter(pedido=pedido).exists():
        messages.warning(request, 'Este pedido ya fue calificado.')
        return redirect('ticket', pedido.id)

    if request.method == 'POST':
        estrellas = int(request.POST.get('estrellas'))
        comentario = request.POST.get('comentario', '')

        Calificacion.objects.create(
            pedido=pedido,
            estrellas=estrellas,
            comentario=comentario
        )

        messages.success(request, 'Gracias por calificar tu compra.')
        return redirect('index')

    # 👇 ESTO FALTABA
    return render(request, 'tienda/calificar.html', {
        'pedido': pedido
    }) 

def buscar_pedidos(request):
    pedidos = None

    if request.method == 'POST':
        email = request.POST.get('email')
        pedidos = Pedido.objects.filter(email=email).order_by('-fecha')

    return render(request, 'tienda/buscar_pedidos.html', {
        'pedidos': pedidos
    })

def login_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['email_cliente'] = email
        return redirect('index')

    return render(request, 'tienda/login_email.html')

def logout_email(request):
    request.session.flush()
    return redirect('index')

def es_admin(user):
    return user.is_staff  # Solo usuarios marcados como staff pueden acceder

@login_required(login_url='/admin/login/')  # Redirige al login si no está logueado
@user_passes_test(es_admin, login_url='/admin/login/')  # Solo admin
def panel_admin(request):
    pedidos = Pedido.objects.all().order_by('-fecha')

    # Datos de ejemplo para gráficas
    dias = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']
    ventas = [150, 200, 180, 220, 170, 250, 300]

    pendientes = Pedido.objects.filter(estado='pendiente').count()
    entregados = Pedido.objects.filter(estado='entregado').count()

    productos_temporada = [p.nombre for p in Producto.objects.all()[:5]]
    cantidad_temporada = [50, 35, 70, 20, 40]

    return render(request, 'tienda/panel_admin.html', {
        'pedidos': pedidos,
        'dias': dias,
        'ventas': ventas,
        'pendientes': pendientes,
        'entregados': entregados,
        'productos_temporada': productos_temporada,
        'cantidad_temporada': cantidad_temporada
    })

@require_POST
def cambiar_estado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = request.POST.get('estado')
    pedido.save()
    return redirect('panel_admin')

def metricas(request):
    total_pedidos = Pedido.objects.count()
    total_ingresos = Pedido.objects.aggregate(Sum('total'))['total__sum'] or 0
    promedio_calificacion = Calificacion.objects.aggregate(
        Avg('estrellas')
    )['estrellas__avg'] or 0

    entregados = Pedido.objects.filter(estado='entregado').count()
    pendientes = Pedido.objects.filter(estado='pendiente').count()

    return render(request, 'tienda/metricas.html', {
        'total_pedidos': total_pedidos,
        'total_ingresos': total_ingresos,
        'promedio_calificacion': round(promedio_calificacion, 1),
        'entregados': entregados,
        'pendientes': pendientes
    })

stripe.api_key = settings.STRIPE_SECRET_KEY

def pago_stripe(request):
    carrito = request.session.get('carrito', [])

    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    intent = stripe.PaymentIntent.create(
        amount=int(total * 100),
        currency='mxn',
        automatic_payment_methods={'enabled': True},
    )

    return render(request, 'tienda/pago_stripe.html', {
        'client_secret': intent.client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'total': total
    })
