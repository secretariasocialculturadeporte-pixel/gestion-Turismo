// frontend/static/js/auth/auth.js
import { fetchAPI } from '../api/api.js';

let token = localStorage.getItem('token');
let user = JSON.parse(localStorage.getItem('user'));

export function getToken() {
    return token;
}

export function getUser() {
    return user;
}

export function handleLogin(e) {
    e.preventDefault();
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;

    fetch('/api/api-token-auth/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput, password: passwordInput }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            token = data.token;
            localStorage.setItem('token', token);
            fetchUser();
        } else {
            alert('Login failed');
        }
    })
    .catch(error => console.error('Error logging in:', error));
}

function fetchUser() {
    fetchAPI('/api/user/')
        .then(data => {
            user = data;
            localStorage.setItem('user', JSON.stringify(user));
            window.dispatchEvent(new CustomEvent('authChange'));
        });
}

export function handleLogout() {
    token = null;
    user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.dispatchEvent(new CustomEvent('authChange'));
}

window.addEventListener('logout', handleLogout);
