console.log('pago.js cargado correctamente');

document.getElementById('form-pago').addEventListener('submit', function (e) {
    e.preventDefault();

    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    if (carrito.length === 0) {
        alert('El carrito está vacío');
        return;
    }

    const direccion = document.getElementById('direccion').value;
    const metodoPago = document.getElementById('metodo').value;
    const email = document.getElementById('email').value;

    fetch('/guardar-pedido/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            carrito: carrito,
            direccion: direccion,
            metodo_pago: metodoPago,
            email: email
        })
    })
    .then(res => res.json())
    .then(data => {
    console.log('RESPUESTA DEL SERVIDOR:', data);

        if (data.ok) {
            localStorage.removeItem('carrito');
            window.location.href = `/ticket/${data.pedido_id}/`;
        } else {
            alert('Error al guardar el pedido');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
});
