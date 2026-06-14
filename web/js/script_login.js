const API = '/api/v1';

let isLogin = true;

function toggleForm() {
    isLogin = !isLogin;
    document.getElementById('formTitle').textContent = isLogin ? 'Войти' : 'Регистрация';
    document.getElementById('formSubtitle').textContent = isLogin ? 'Войдите в аккаунт' : 'Создайте новый аккаунт';
    document.getElementById('name').classList.toggle('hidden', isLogin);
    document.getElementById('submitBtn').textContent = isLogin ? 'Войти' : 'Зарегистрироваться';
    document.getElementById('toggleBtn').textContent = isLogin ? 'Нет аккаунта? Регистрация' : 'Уже есть аккаунт? Войти';
    document.getElementById('errorMsg').textContent = '';
}

async function submitForm() {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const name = document.getElementById('name').value.trim();

    if (!email || !password) { showError('Заполните все поля'); return; }

    if (isLogin) {
        await login(email, password);
    } else {
        if (!name) { showError('Введите имя'); return; }
        await register(name, email, password);
    }
}

async function login(email, password) {
    try {
        const res = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (!res.ok) { showError(data.detail || 'Ошибка входа'); return; }
        localStorage.setItem('token', data.access_token);
        window.location.href = 'index.html';
    } catch (e) {
        showError('Ошибка соединения с сервером');
    }
}

async function register(name, email, password) {
    try {
        const res = await fetch(`${API}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: name, email, password })
        });
        const data = await res.json();
        if (!res.ok) { showError(data.detail || 'Ошибка регистрации'); return; }
        alert('Регистрация успешна! Войдите в аккаунт.');
        toggleForm();
    } catch (e) {
        showError('Ошибка соединения с сервером');
    }
}

function showError(msg) {
    document.getElementById('errorMsg').textContent = msg;
}

function checkAuth() {
    const token = localStorage.getItem('token');
    const currentPage = window.location.pathname.split('/').pop();
    if (token && currentPage === 'login.html') {
        window.location.href = 'index.html';
    }
}

document.addEventListener('DOMContentLoaded', checkAuth);