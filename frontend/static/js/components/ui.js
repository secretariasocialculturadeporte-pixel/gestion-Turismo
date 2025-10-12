// frontend/static/js/components/ui.js
import { getUser } from '../auth/auth.js';
import { renderHome, renderTurismo, renderEmpleo, renderFeedback, renderAdminDashboard, renderBusinessDashboard } from '../views/views.js';

const mainNav = document.getElementById('main-nav');
const mainContent = document.getElementById('main-content');
const authContainer = document.getElementById('auth-container');
const userContainer = document.getElementById('user-container');
const userInfo = document.getElementById('user-info');
const appContainer = document.getElementById('app-container');

const viewPermissions = {
    1: ['home', 'turismo', 'empleo', 'feedback', 'admin'], // SuperAdmin
    2: ['home', 'turismo', 'empleo', 'feedback', 'dashboard'], // AdminMunicipal
    3: ['home', 'turismo', 'empleo', 'feedback', 'dashboard'], // PropietarioEmpresa
    4: ['home', 'turismo', 'empleo', 'feedback'], // Ciudadano
};

export function updateUI() {
    const user = getUser();
    if (user) {
        authContainer.style.display = 'none';
        userContainer.style.display = 'block';
        appContainer.style.display = 'flex';
        userInfo.textContent = user.username;
        buildNav();
    } else {
        authContainer.style.display = 'block';
        userContainer.style.display = 'none';
        appContainer.style.display = 'none';
        mainContent.innerHTML = '';
    }
}

function buildNav() {
    mainNav.innerHTML = '';
    const user = getUser();
    const userRole = user.rol;
    const allowedViews = viewPermissions[userRole] || [];

    allowedViews.forEach(view => {
        const button = document.createElement('button');
        button.dataset.view = view;
        button.textContent = view.charAt(0).toUpperCase() + view.slice(1);
        mainNav.appendChild(button);
    });
}

export function handleNavClick(e) {
    if (e.target.tagName === 'BUTTON') {
        const view = e.target.dataset.view;
        navigateTo(view);
    }
}

export function navigateTo(view) {
    mainContent.innerHTML = `<h2>Loading ${view}...</h2>`;
    const user = getUser();
    const userRole = user.rol;
    const allowedViews = viewPermissions[userRole] || [];

    if (!allowedViews.includes(view)) {
        mainContent.innerHTML = '<h2>Access Denied</h2>';
        return;
    }

    switch (view) {
        case 'home':
            renderHome(mainContent);
            break;
        case 'turismo':
            renderTurismo(mainContent);
            break;
        case 'empleo':
            renderEmpleo(mainContent);
            break;
        case 'feedback':
            renderFeedback(mainContent);
            break;
        case 'admin':
            renderAdminDashboard(mainContent);
            break;
        case 'dashboard':
            renderBusinessDashboard(mainContent);
            break;
        default:
            mainContent.innerHTML = '<h2>Page not found</h2>';
    }
}

export function showNotification(message, isError = false) {
    const notification = document.createElement('div');
    notification.className = `notification ${isError ? 'error' : ''}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.classList.add('show');
    }, 10); // Small delay to allow the element to be in the DOM

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 500); // Wait for the transition to finish
    }, 3000);
}
