// frontend/static/js/app.js
import { handleLogin, handleLogout, getToken, getUser } from './auth/auth.js';
import { updateUI, handleNavClick, navigateTo } from './components/ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');
    const mainNav = document.getElementById('main-nav');

    // Initial UI update
    updateUI();

    // Event Listeners
    loginForm.addEventListener('submit', handleLogin);
    logoutButton.addEventListener('click', handleLogout);
    mainNav.addEventListener('click', handleNavClick);

    // Listen for auth changes
    window.addEventListener('authChange', () => {
        updateUI();
        if (getToken()) {
            navigateTo('home');
        }
    });

    // Initial navigation if logged in
    if (getToken() && getUser()) {
        navigateTo('home');
    }
});
