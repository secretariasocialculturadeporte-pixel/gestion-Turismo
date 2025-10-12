// frontend/static/js/views/views.js
import { fetchAPI } from '../api/api.js';
import { showNotification } from '../components/ui.js';
import { getUser } from '../auth/auth.js';

export function renderHome(mainContent) {
    mainContent.innerHTML = '<h2>Departamentos de Colombia</h2><ul id="departamentos-list"></ul>';
    const list = document.getElementById('departamentos-list');
    fetchAPI('/api/departamentos/')
        .then(data => {
            list.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.nombre_departamento;
                list.appendChild(li);
            });
        });
}

export function renderTurismo(mainContent) {
    mainContent.innerHTML = '<h2>Turismo</h2><h3>Atractivos Turísticos</h3><ul id="atractivos-list"></ul><h3>Eventos Turísticos</h3><ul id="eventos-list"></ul><div id="item-details" class="modal"></div>';
    const atractivosList = document.getElementById('atractivos-list');
    const eventosList = document.getElementById('eventos-list');

    fetchAPI('/api/atractivos/')
        .then(data => {
            atractivosList.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.nombre_atractivo;
                li.dataset.id = item.id;
                li.dataset.type = 'atractivo';
                atractivosList.appendChild(li);
            });
        });

    fetchAPI('/api/eventos/')
        .then(data => {
            eventosList.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.nombre_evento;
                li.dataset.id = item.id;
                li.dataset.type = 'evento';
                eventosList.appendChild(li);
            });
        });

    atractivosList.addEventListener('click', (e) => handleItemClick(e, mainContent));
    eventosList.addEventListener('click', (e) => handleItemClick(e, mainContent));
}

function handleItemClick(e, mainContent) {
    if (e.target.tagName === 'LI') {
        const id = e.target.dataset.id;
        const type = e.target.dataset.type;
        const itemDetails = mainContent.querySelector('#item-details');
        itemDetails.style.display = 'block';

        const content = document.createElement('div');
        content.className = 'modal-content';

        const closeButton = document.createElement('span');
        closeButton.className = 'close';
        closeButton.innerHTML = '&times;';
        closeButton.onclick = () => {
            itemDetails.style.display = 'none';
        };
        content.appendChild(closeButton);

        if (type === 'atractivo') {
            fetchAPI(`/api/atractivos/${id}/`)
                .then(data => {
                    content.innerHTML += `<h4>${data.nombre_atractivo}</h4><p>${data.descripcion_breve}</p>`;
                    itemDetails.innerHTML = '';
                    itemDetails.appendChild(content);
                });
        } else if (type === 'evento') {
            fetchAPI(`/api/eventos/${id}/`)
                .then(data => {
                    content.innerHTML += `<h4>${data.nombre_evento}</h4><p>${data.descripcion}</p><p>Start Date: ${data.fecha_inicio}</p><p>End Date: ${data.fecha_fin}</p>`;
                    itemDetails.innerHTML = '';
                    itemDetails.appendChild(content);
                });
        }
    }
}

export function renderEmpleo(mainContent) {
    mainContent.innerHTML = '<h2>Empleo</h2><ul id="vacantes-list"></ul>';
    const list = document.getElementById('vacantes-list');
    fetchAPI('/api/vacantes/')
        .then(data => {
            list.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.titulo_vacante;
                list.appendChild(li);
            });
        });
}

export function renderFeedback(mainContent) {
    mainContent.innerHTML = `
        <h2>Feedback</h2>
        <form id="feedback-form">
            <textarea id="feedback-text" placeholder="Enter your feedback" required></textarea>
            <button type="submit">Submit Feedback</button>
        </form>
    `;
    const feedbackForm = document.getElementById('feedback-form');
    feedbackForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const feedbackText = document.getElementById('feedback-text').value;
        console.log('Feedback submitted:', feedbackText);
        showNotification('Feedback submitted!');
        feedbackForm.reset();
    });
}

export function renderAdminDashboard(mainContent) {
    const user = getUser();
    mainContent.innerHTML = `
        <h2>Admin Dashboard</h2>
        <h3>Empresas</h3>
        ${user.rol === 1 ? '<button id="create-empresa-btn">Create New Empresa</button>' : ''}
        <ul id="empresas-list"></ul>
        <div id="empresa-form-container"></div>
    `;
    const list = document.getElementById('empresas-list');
    const createButton = document.getElementById('create-empresa-btn');
    const formContainer = document.getElementById('empresa-form-container');

    if (createButton) {
        createButton.addEventListener('click', () => {
            renderEmpresaForm(formContainer);
        });
    }

    fetchAPI('/api/empresas/')
        .then(data => {
            list.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.razon_social_o_nombre_comercial;

                if (user.rol === 1) { // SuperAdmin
                    const editButton = document.createElement('button');
                    editButton.textContent = 'Edit';
                    editButton.addEventListener('click', () => {
                        renderEmpresaForm(formContainer, item);
                    });
                    li.appendChild(editButton);

                    const deleteButton = document.createElement('button');
                    deleteButton.textContent = 'Delete';
                    deleteButton.addEventListener('click', () => {
                        if (confirm('Are you sure you want to delete this empresa?')) {
                            fetchAPI(`/api/empresas/${item.id}/`, { method: 'DELETE' })
                                .then(() => {
                                    renderAdminDashboard(mainContent); // Refresh the list
                                    showNotification('Empresa deleted successfully.');
                                });
                        }
                    });
                    li.appendChild(deleteButton);
                }

                list.appendChild(li);
            });
        });
}

function renderEmpresaForm(container, empresa = null) {
    container.innerHTML = `
        <h4>${empresa ? 'Edit' : 'Create'} Empresa</h4>
        <form id="empresa-form">
            <input type="text" id="razon_social" placeholder="Razon Social" value="${empresa ? empresa.razon_social_o_nombre_comercial : ''}" required>
            <input type="text" id="nit" placeholder="NIT" value="${empresa ? empresa.nit : ''}">
            <input type="text" id="tipo_prestador" placeholder="Tipo Prestador" value="${empresa ? empresa.tipo_prestador : ''}" required>
            <button type="submit">${empresa ? 'Update' : 'Create'}</button>
        </form>
    `;

    const form = document.getElementById('empresa-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const razonSocial = document.getElementById('razon_social').value;
        const tipoPrestador = document.getElementById('tipo_prestador').value;
        const nit = document.getElementById('nit').value;

        if (!razonSocial || !tipoPrestador) {
            showNotification('Razon Social and Tipo Prestador are required.', true);
            return;
        }

        if (nit && !/^\d+$/.test(nit)) {
            showNotification('NIT must be a number.', true);
            return;
        }

        const formData = {
            razon_social_o_nombre_comercial: razonSocial,
            nit: nit,
            tipo_prestador: tipoPrestador,
            municipio: '05001' // Hardcoded for now, should be a select
        };

        const url = empresa ? `/api/empresas/${empresa.id}/` : '/api/empresas/';
        const method = empresa ? 'PUT' : 'POST';

        fetchAPI(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        }).then(() => {
            renderAdminDashboard(document.getElementById('main-content')); // Refresh the list
            showNotification(`Empresa ${empresa ? 'updated' : 'created'} successfully.`);
        });
    });
}

export function renderBusinessDashboard(mainContent) {
    const user = getUser();
    mainContent.innerHTML = `
        <h2>Business Dashboard</h2>
        <div id="business-info"></div>
        <h3>Products and Events</h3>
        <button id="create-product-btn">Create New Product/Event</button>
        <ul id="products-list"></ul>
        <div id="product-form-container"></div>
    `;
    const businessInfo = document.getElementById('business-info');
    const productsList = document.getElementById('products-list');
    const createButton = document.getElementById('create-product-btn');
    const formContainer = document.getElementById('product-form-container');

    createButton.addEventListener('click', () => {
        renderProductForm(formContainer);
    });

    fetchAPI(`/api/empresas/${user.empresa_asociada}/`)
        .then(data => {
            businessInfo.innerHTML = `<h3>${data.razon_social_o_nombre_comercial}</h3>`;
        });

    fetchAPI(`/api/productos-eventos/?empresa=${user.empresa_asociada}`)
        .then(data => {
            productsList.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.nombre} (${item.tipo})`;

                const editButton = document.createElement('button');
                editButton.textContent = 'Edit';
                editButton.addEventListener('click', () => {
                    renderProductForm(formContainer, item);
                });
                li.appendChild(editButton);

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.addEventListener('click', () => {
                    if (confirm('Are you sure you want to delete this item?')) {
                        fetchAPI(`/api/productos-eventos/${item.id}/`, { method: 'DELETE' })
                            .then(() => {
                                renderBusinessDashboard(mainContent); // Refresh the list
                                showNotification('Item deleted successfully.');
                            });
                    }
                });
                li.appendChild(deleteButton);

                productsList.appendChild(li);
            });
        });
}

function renderProductForm(container, product = null) {
    container.innerHTML = `
        <h4>${product ? 'Edit' : 'Create'} Product/Event</h4>
        <form id="product-form">
            <input type="text" id="nombre" placeholder="Name" value="${product ? product.nombre : ''}" required>
            <input type="text" id="descripcion" placeholder="Description" value="${product ? product.descripcion : ''}">
            <select id="tipo" required>
                <option value="Producto" ${product && product.tipo === 'Producto' ? 'selected' : ''}>Product</option>
                <option value="Evento" ${product && product.tipo === 'Evento' ? 'selected' : ''}>Event</option>
            </select>
            <input type="number" id="precio" placeholder="Price" value="${product ? product.precio : ''}">
            <input type="date" id="fecha_evento" value="${product ? product.fecha_evento : ''}">
            <button type="submit">${product ? 'Update' : 'Create'}</button>
        </form>
    `;

    const form = document.getElementById('product-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const user = getUser();

        const nombre = document.getElementById('nombre').value;
        const tipo = document.getElementById('tipo').value;
        const precio = document.getElementById('precio').value;

        if (!nombre || !tipo) {
            showNotification('Name and Type are required.', true);
            return;
        }

        if (precio && !/^\d+(\.\d{1,2})?$/.test(precio)) {
            showNotification('Price must be a valid number.', true);
            return;
        }

        const formData = {
            nombre: nombre,
            descripcion: document.getElementById('descripcion').value,
            tipo: tipo,
            precio: precio,
            fecha_evento: document.getElementById('fecha_evento').value,
            empresa: user.empresa_asociada
        };

        const url = product ? `/api/productos-eventos/${product.id}/` : '/api/productos-eventos/';
        const method = product ? 'PUT' : 'POST';

        fetchAPI(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        }).then(() => {
            renderBusinessDashboard(document.getElementById('main-content')); // Refresh the list
            showNotification(`Item ${product ? 'updated' : 'created'} successfully.`);
        });
    });
}
