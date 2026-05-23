let currentUser = null;
let posts = [];
let isLogin = true;

    function toggleForm() {
      isLogin = !isLogin;
      
      document.getElementById('formTitle').textContent = isLogin ? 'Вход в систему' : 'Регистрация';
      document.getElementById('formSubtitle').textContent = isLogin ? 'Планирование публикаций' : 'Создайте новый аккаунт';
      document.getElementById('name').classList.toggle('hidden', isLogin);
      document.getElementById('submitBtn').textContent = isLogin ? 'Войти' : 'Зарегистрироваться';
      document.getElementById('toggleBtn').textContent = isLogin ? 
        'Нет аккаунта? Зарегистрироваться' : 
        'Уже есть аккаунт? Войти';
    }

    async function submitForm() {
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value.trim();
      const name = document.getElementById('name').value.trim();

      if (!email || !password) {
        alert('Заполните email и пароль');
        return;
      }

      if (!isLogin && !name) {
        alert('Введите ваше имя');
        return;
      }

      if (isLogin) {
        await login(email, password);
      } else {
        await register(name, email, password);
      }
    }
// Хэширование пароля
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Регистрация нового пользователя
async function register(name, email, password) {
  let users = JSON.parse(localStorage.getItem('users')) || [];

  // Проверка, существует ли email
  if (users.some(u => u.email === email)) {
    alert('Пользователь с таким email уже существует');
    return;
  }

  const passwordHash = await hashPassword(password);

  const newUser = {
    id: Date.now(),
    name: name,
    email: email,
    passwordHash: passwordHash,
    role: "user"   // по умолчанию обычный пользователь
  };

  users.push(newUser);
  localStorage.setItem('users', JSON.stringify(users));

  alert('Регистрация прошла успешно! Теперь вы можете войти.');
  toggleForm(); // переключаем обратно на форму входа
}

// Логин
async function login(email, password) {
  const users = JSON.parse(localStorage.getItem('users')) || [];
  
  for (let user of users) {
    const inputHash = await hashPassword(password);
    if (user.email === email && user.passwordHash === inputHash) {
      currentUser = { 
        id: user.id, 
        name: user.name, 
        email: user.email, 
        role: user.role 
      };
      
      saveData();
      window.location.href = 'index.html';
      return;
    }
  }

  alert('Неверный email или пароль');
}

// Логин (вызывается из login.html)
function login() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value.trim();

  const users = [
    { id: 1, email: "moderator@demo.ru", password: "123456", name: "Модератор", role: "moderator" },
    { id: 2, email: "user@demo.ru", password: "123456", name: "Алексей Иванов", role: "user" }
  ];

  const user = users.find(u => u.email === email && u.password === password);

  if (user) {
    currentUser = user;
    saveData();
    window.location.href = 'index.html';
  } else {
    alert('Неверный email или пароль');
  }
}

function checkAuth() {
  loadData(); // загружаем currentUser из localStorage

  const currentPage = window.location.pathname.split('/').pop();

  // Если пользователь НЕ авторизован
  if (currentUser) {
    if (currentPage === 'login.html') {
      window.location.href = 'index.html';
      return true;
    }
  }
}

function saveData() {
  localStorage.setItem('posts', JSON.stringify(posts));
  if (currentUser) localStorage.setItem('currentUser', JSON.stringify(currentUser));
}

document.addEventListener('DOMContentLoaded', () => {
    checkAuth()
});