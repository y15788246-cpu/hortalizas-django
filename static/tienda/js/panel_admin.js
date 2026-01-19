// ---------------- BÚSQUEDA INSTANTÁNEA ----------------
const input = document.getElementById('busqueda');
const tabla = document.getElementById('tabla-pedidos');
const contador = document.getElementById('contador');

function limpiarResaltado(fila) {
    const celdas = fila.getElementsByTagName('td');
    for (let celda of celdas) {
        celda.innerHTML = celda.textContent;
    }
}

function resaltarTexto(fila, texto) {
    const celdas = fila.getElementsByTagName('td');
    const regex = new RegExp(`(${texto})`, 'gi');
    for (let celda of celdas) {
        celda.innerHTML = celda.textContent.replace(regex, '<span style="background-color: yellow;">$1</span>');
    }
}

function filtrarFilas() {
    const filtro = input.value.toLowerCase();
    let visibles = 0;

    const filas = tabla.getElementsByTagName('tr');
    for (let fila of filas) {
        limpiarResaltado(fila);
        const celdas = fila.getElementsByTagName('td');
        let textoFila = '';
        for (let celda of celdas) {
            textoFila += celda.textContent.toLowerCase() + ' ';
        }

        if (textoFila.indexOf(filtro) > -1) {
            fila.style.display = '';
            visibles++;
            if (filtro) resaltarTexto(fila, filtro);
        } else {
            fila.style.display = 'none';
        }
    }

    contador.textContent = visibles ? `${visibles} pedido(s) encontrados` : 'No hay resultados';
}

// Evento de búsqueda
input.addEventListener('keyup', filtrarFilas);

// Observador de cambios (para nuevas filas dinámicas)
const observer = new MutationObserver(filtrarFilas);
observer.observe(tabla, { childList: true });

// ---------------- GRÁFICAS CHART.JS ----------------
const ventasCtx = document.getElementById('ventasChart').getContext('2d');
const estadoCtx = document.getElementById('estadoChart').getContext('2d');
const productosCtx = document.getElementById('productosChart').getContext('2d');

// Gráfica de Ventas por día
new Chart(ventasCtx, {
    type: 'bar',
    data: {
        labels: window.dias || [],          // Lista de días desde Django
        datasets: [{
            label: 'Ventas',
            data: window.ventas || [],      // Datos de ventas desde Django
            backgroundColor: 'rgba(75, 192, 192, 0.6)'
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: false } }
    }
});

// Gráfica de Pedidos por estado
new Chart(estadoCtx, {
    type: 'doughnut',
    data: {
        labels: ['Pendientes', 'Entregados'],
        datasets: [{
            data: [window.pendientes || 0, window.entregados || 0],
            backgroundColor: ['#ffcc00', '#4caf50']
        }]
    },
    options: { responsive: true }
});

// Gráfica de Productos más vendidos por temporada
new Chart(productosCtx, {
    type: 'bar',
    data: {
        labels: window.productos_temporada || [],
        datasets: [{
            label: 'Cantidad vendida',
            data: window.cantidad_temporada || [],
            backgroundColor: 'rgba(153, 102, 255, 0.6)'
        }]
    },
    options: { responsive: true }
});
