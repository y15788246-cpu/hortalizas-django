document.addEventListener('DOMContentLoaded', () => {

    const botones = document.querySelectorAll('.btn-agregar');

    botones.forEach(boton => {
        boton.addEventListener('click', () => {

            const producto = {
                id: boton.dataset.id,
                nombre: boton.dataset.nombre,
                precio: parseFloat(boton.dataset.precio),
                imagen: boton.dataset.imagen,
                cantidad: 1
            };

            agregarAlCarrito(producto);
            alert('Producto agregado al carrito');
            actualizarContador();
        });
    });

});

function agregarAlCarrito(producto) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    const existe = carrito.find(p => p.id === producto.id);

    if (existe) {
        existe.cantidad++;
    } else {
        carrito.push(producto);
    }

    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarContador();
}

function mostrarCarrito() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const contenedor = document.getElementById('carrito');
    const totalSpan = document.getElementById('total');

    if (!contenedor) return;

    contenedor.innerHTML = '';
    let total = 0;

    carrito.forEach((producto, index) => {
        const subtotal = producto.precio * producto.cantidad;
        total += subtotal;

        contenedor.innerHTML += `
            <div class="item">
                <img src="${producto.imagen}" width="80">
                <strong>${producto.nombre}</strong>
                <p>$${producto.precio} / unidad</p>

                <div class="cantidad">
                    <button onclick="cambiarCantidad(${index}, -1)">−</button>
                    <span>${producto.cantidad}</span>
                    <button onclick="cambiarCantidad(${index}, 1)">+</button>
                </div>

                <p>Subtotal: $${subtotal.toFixed(2)}</p>
                <button onclick="eliminarProducto(${index})">Eliminar</button>
            </div>
        `;
    });

    totalSpan.textContent = total.toFixed(2);
}

function eliminarProducto(index) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    carrito.splice(index, 1);
    localStorage.setItem('carrito', JSON.stringify(carrito));
    mostrarCarrito();
    actualizarContador();
}

function cambiarCantidad(index, cambio) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    carrito[index].cantidad += cambio;

    if (carrito[index].cantidad <= 0) {
        carrito.splice(index, 1);
    }

    localStorage.setItem('carrito', JSON.stringify(carrito));
    mostrarCarrito();
    actualizarContador();
}

function actualizarContador() {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const contador = document.getElementById('contador-carrito');

    if (!contador) return;

    let totalProductos = 0;
    carrito.forEach(producto => {
        totalProductos += producto.cantidad;
    });

    contador.textContent = totalProductos;
}

botones.forEach(boton => {
boton.addEventListener('click', () => {

    const producto = {
        id: boton.dataset.id,
        nombre: boton.dataset.nombre,
        precio: parseFloat(boton.dataset.precio),
        imagen: boton.dataset.imagen,
        cantidad: 1
    };

    const stockDisponible = parseInt(boton.dataset.stock);
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const existente = carrito.find(p => p.id === producto.id);

    if (existente && existente.cantidad >= stockDisponible) {
        alert('No hay más stock disponible');
        return;
    }

    agregarAlCarrito(producto);

    boton.classList.add('animar');
    setTimeout(() => boton.classList.remove('animar'), 300);

    actualizarContador();
});
});

document.addEventListener('DOMContentLoaded', actualizarContador);
