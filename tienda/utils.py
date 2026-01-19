from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def enviar_ticket_por_correo(pedido, detalles, email_cliente):
    html = render_to_string('tienda/ticket_pdf.html', {
        'pedido': pedido,
        'detalles': detalles
    })

    pdf = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf)

    correo = EmailMessage(
        subject=f'Ticket de compra - Pedido #{pedido.id}',
        body='Gracias por su compra. Adjuntamos su ticket.',
        from_email=None,
        to=[email_cliente],
    )

    correo.attach(
        f'ticket_{pedido.id}.pdf',
        pdf.getvalue(),
        'application/pdf'
    )
    
    print("INTENTANDO ENVIAR A:", email_cliente)
    correo.send()
