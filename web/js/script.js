let posts = [];
let currentFilter = { status: 'all', tag: 'all', sort: 'date-desc' };

// Загрузка данных
function loadData() {
  const savedPosts = localStorage.getItem('posts');
  const savedUser = localStorage.getItem('currentUser');

  if (savedPosts) posts = JSON.parse(savedPosts);
  if (savedUser) currentUser = JSON.parse(savedUser);
}

// Сохранение данных
function saveData() {
  localStorage.setItem('posts', JSON.stringify(posts));
  if (currentUser) localStorage.setItem('currentUser', JSON.stringify(currentUser));
}

// Проверка авторизации
// Проверка авторизации
function checkAuth() {
  loadData(); // загружаем currentUser из localStorage

  const currentPage = window.location.pathname.split('/').pop();

  // Если пользователь НЕ авторизован
  if (!currentUser) {
    window.location.href = 'login.html';
    return false;
  }

  // Если пользователь АВТОРИЗОВАН
  else {
    // Если мы на странице логина — перебрасываем на главную
    if (currentPage === 'login.html') {
      window.location.href = 'index.html';
      return true;
    }
    // На всех остальных страницах — разрешаем загрузку
    return true;
  }
}

// Выход
function logout() {
  localStorage.removeItem('currentUser');
  window.location.href = 'login.html';
}

// Рендер бокового меню в зависимости от роли
function renderSidebar() {
  const menu = document.getElementById('sidebarMenu');
  menu.innerHTML = `
    <div onclick="loadPage('dashboard')" class="menu-item active flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer">
      <i class="fas fa-home w-5"></i><span>Главная</span>
    </div>
    <div onclick="loadPage('posts')" class="menu-item flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer">
      <i class="fas fa-file-alt w-5"></i><span>Все публикации</span>
    </div>
    <div onclick="loadPage('calendar')" class="menu-item flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer">
      <i class="fas fa-calendar w-5"></i><span>Календарь</span>
    </div>
    <div onclick="loadPage('tags')" class="menu-item flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer">
      <i class="fas fa-tags w-5"></i><span>Теги</span>
    </div>
  `;

  if (currentUser.role === 'moderator') {
    menu.innerHTML += `
      <div onclick="loadPage('moderation')" class="menu-item flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer">
        <i class="fas fa-user-shield w-5"></i><span>Модерация</span>
      </div>
    `;
  }
}

// Главная страница (дашборд)
function renderDashboard() {
  const main = document.getElementById('mainContent');
  const head = document.getElementById('rec_header');
  head.innerHTML = `<h1 class="text-2xl font-semibold text-gray-900" id="rec_header">Добро пожаловать, ${currentUser.name}!</h1>`;
  main.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-3xl shadow-sm">
        <h3 class="text-gray-500">Всего публикаций</h3>
        <p class="text-5xl font-semibold mt-2">${posts.length}</p>
      </div>
      <div class="bg-white p-6 rounded-3xl shadow-sm">
        <h3 class="text-gray-500">Ожидают модерации</h3>
        <p class="text-5xl font-semibold mt-2 text-amber-600">${posts.filter(p => p.status === 'moderation').length}</p>
      </div>
      <div class="bg-white p-6 rounded-3xl shadow-sm">
        <h3 class="text-gray-500">Опубликовано</h3>
        <p class="text-5xl font-semibold mt-2 text-emerald-600">${posts.filter(p => p.status === 'published').length}</p>
      </div>
    </div>
  `;
}

// Список публикаций
function renderPosts(filter = currentFilter) {
  const head = document.getElementById('rec_header');
  head.innerHTML = `<h1 class="text-2xl font-semibold text-gray-900" id="rec_header">Рекламные Кампании</h1>`;
  const main = document.getElementById('mainContent');
  
  let filteredPosts = posts.filter(post => {
    if (filter.status !== 'all' && post.status !== filter.status) return false;
    return true;
  });

  // Сортировка
  if (filter.sort === 'date-desc') {
    filteredPosts.sort((a, b) => new Date(b.scheduledDate) - new Date(a.scheduledDate));
  } else if (filter.sort === 'date-asc') {
    filteredPosts.sort((a, b) => new Date(a.scheduledDate) - new Date(b.scheduledDate));
  }

  let html = `<div class="grid grid-cols-1 lg:grid-cols-1 gap-6">`;

  filteredPosts.forEach(post => {
    const statusClass = post.status === 'published' ? 'bg-emerald-100 text-emerald-700' : 
                       post.status === 'moderation' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600';
    
    html += `
      <div class="pub-card bg-white rounded-3xl p-6 shadow-sm cursor-pointer hover:shadow-md" onclick="viewPost(${post.id})">
        <div class="flex justify-between items-start">
          <h3 class="font-semibold text-lg leading-tight">${post.title}</h3>
          <span class="text-xs px-3 py-1 rounded-full ${statusClass}">
            ${post.status === 'published' ? 'Опубликовано' : post.status === 'moderation' ? 'На модерации' : 'Черновик'}
          </span>
        </div>
        <p class="text-gray-500 text-sm mt-4 line-clamp-2">${post.text.substring(0, 120)}...</p>
        <div class="flex flex-wrap gap-2 mt-4">
          ${post.tags.map(tag => `<span class="text-xs bg-gray-100 px-3 py-1 rounded-full">#${tag}</span>`).join('')}
        </div>
        <div class="text-xs text-gray-400 mt-6">
          ${new Date(post.scheduledDate).toLocaleString('ru-RU')}
        </div>
      </div>
    `;
  });

  html += `</div>`;
  main.innerHTML = html;
}

// Просмотр одного поста
function viewPost(id) {
  const post = posts.find(p => p.id === id);
  if (!post) return;

  const main = document.getElementById('detailPanel');
  main.innerHTML = `
    <button onclick="loadPage('posts')" class="mb-6 text-emerald-600 hover:underline flex items-center gap-2">
      ← Назад к списку
    </button>
    <div class="bg-white rounded-3xl p-10 max-w-4xl mx-auto">
      <h1 class="text-3xl font-semibold">${post.title}</h1>
      <p class="text-gray-500 mt-2">${new Date(post.scheduledDate).toLocaleString('ru-RU')}</p>
      
      ${post.media && post.media.length ? `<img src="${post.media[0]}" class="w-full rounded-2xl mt-8">` : ''}
      
      <div class="prose mt-8">${post.text}</div>
      
      <div class="mt-10 flex gap-4">
        ${currentUser.role === 'moderator' && post.status === 'moderation' ? `
          <button onclick="approvePost(${post.id})" class="flex-1 bg-emerald-600 text-white py-4 rounded-2xl font-medium">Одобрить и опубликовать</button>
          <button onclick="rejectPost(${post.id})" class="flex-1 border border-red-300 text-red-600 py-4 rounded-2xl font-medium">Отправить на доработку</button>
        ` : ''}
      </div>
    </div>
  `;
}

// Создание новой публикации
function renderNewPost() {
  const main = document.getElementById('mainContent');
  const modal = document.getElementById('card-modal');
  const body = document.getElementById('modal-body');
  body.innerHTML = `
    <h1 class="text-3xl font-semibold mb-8">Новая публикация</h1>
    <div class="max-w-2xl bg-white rounded-3xl p-10">
      <input id="postTitle" type="text" placeholder="Заголовок публикации" class="w-full px-5 py-4 border border-gray-300 rounded-2xl text-lg mb-6">
      <textarea id="postText" rows="6" placeholder="Текст публикации..." class="w-full px-5 py-4 border border-gray-300 rounded-2xl mb-6"></textarea>
      
      <input id="postMedia" type="text" placeholder="Ссылка на изображение / видео" class="w-full px-5 py-4 border border-gray-300 rounded-2xl mb-6">
      
      <input id="postTags" type="text" placeholder="Теги через запятую (продажи, эксперт, акция)" class="w-full px-5 py-4 border border-gray-300 rounded-2xl mb-6">
      
      <input id="postDate" type="datetime-local" class="w-full px-5 py-4 border border-gray-300 rounded-2xl mb-8">
      
      <button onclick="createPost()" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-4 rounded-2xl text-lg font-medium">
        Создать публикацию
      </button>
    </div>
  `;
  modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('card-modal').style.display = 'none';
}

// Создание поста
function createPost() {
  const title = document.getElementById('postTitle').value.trim();
  const text = document.getElementById('postText').value.trim();
  const media = document.getElementById('postMedia').value.trim();
  const tagsStr = document.getElementById('postTags').value.trim();
  const scheduledDate = document.getElementById('postDate').value;

  if (!title || !text || !scheduledDate) {
    alert('Заполните обязательные поля');
    return;
  }

  const newPost = {
    id: Date.now(),
    title,
    text,
    media: media ? [media] : [],
    tags: tagsStr ? tagsStr.split(',').map(t => t.trim()) : [],
    scheduledDate,
    status: currentUser.role === 'moderator' ? 'published' : 'moderation',
    authorId: currentUser.id,
    createdAt: new Date().toISOString()
  };

  posts.unshift(newPost);
  saveData();
  alert('Публикация успешно создана!');
  loadPage('posts');
}

// Модерация
function renderModeration() {
  if (currentUser.role !== 'moderator') {
    alert('Доступ запрещён');
    return;
  }

  const moderationPosts = posts.filter(p => p.status === 'moderation');

  const main = document.getElementById('mainContent');
  const head = document.getElementById('rec_header');
  head.innerHTML = `<h1 class="text-2xl font-semibold text-gray-900" id="rec_header">Модерация публикаций</h1>`;

  if (moderationPosts.length === 0) {
    main.innerHTML += `<p class="text-gray-500">Нет публикаций на модерации</p>`;
    return;
  }

  moderationPosts.forEach(post => {
    const div = document.createElement('div');
    div.className = "bg-white p-6 rounded-3xl mb-6";
    div.innerHTML = `
      <h3 class="font-semibold">${post.title}</h3>
      <p class="text-sm text-gray-500 mt-2">${post.text.substring(0, 150)}...</p>
      <div class="mt-6 flex gap-4">
        <button onclick="approvePost(${post.id}); this.parentElement.parentElement.remove()" class="px-6 py-3 bg-emerald-600 text-white rounded-2xl">Одобрить</button>
        <button onclick="rejectPost(${post.id}); this.parentElement.parentElement.remove()" class="px-6 py-3 border border-red-300 text-red-600 rounded-2xl">Отклонить</button>
      </div>
    `;
    main.appendChild(div);
  });
}

function approvePost(id) {
  const post = posts.find(p => p.id === id);
  if (post) {
    post.status = 'published';
    saveData();
    alert('Публикация одобрена и запланирована!');
  }
}

function rejectPost(id) {
  if (confirm('Отправить пост на доработку?')) {
    const post = posts.find(p => p.id === id);
    if (post) {
      post.status = 'draft';
      saveData();
      alert('Пост отправлен автору на доработку');
    }
  }
}

function renderCalendar() {
  const main = document.getElementById('mainContent');
  
  const today = new Date();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();
  document.getElementById('rec_header').innerHTML = `<h1 class="text-2xl font-semibold text-gray-900" id="rec_header">Календарь публикаций</h1>`;
  let html = `
    <div class="bg-white rounded-3xl p-8 shadow-sm">
      <div class="flex justify-between items-center mb-6">
        <button onclick="prevMonth()" class="text-2xl px-4 py-2 hover:bg-gray-100 rounded-xl">‹</button>
        <h2 id="calendarTitle" class="text-2xl font-medium">Май 2026</h2>
        <button onclick="nextMonth()" class="text-2xl px-4 py-2 hover:bg-gray-100 rounded-xl">›</button>
      </div>
      
      <div class="grid grid-cols-7 gap-2 text-center text-sm font-medium text-gray-500 mb-2">
        <div>Пн</div><div>Вт</div><div>Ср</div><div>Чт</div><div>Пт</div><div>Сб</div><div>Вс</div>
      </div>
      
      <div id="calendarGrid" class="grid grid-cols-7 gap-2"></div>
    </div>
  `;

  main.innerHTML = html;
  renderCalendarGrid(currentMonth, currentYear);
}

// Глобальные переменные для календаря
let calendarMonth = new Date().getMonth();
let calendarYear = new Date().getFullYear();

function renderCalendarGrid(month, year) {
  const grid = document.getElementById('calendarGrid');
  grid.innerHTML = '';

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Пустые ячейки в начале
  for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
    grid.innerHTML += `<div class="h-24"></div>`;
  }

  // Дни месяца
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    const postsOnDay = posts.filter(p => p.scheduledDate.startsWith(dateStr));

    const isToday = day === new Date().getDate() && 
                    month === new Date().getMonth() && 
                    year === new Date().getFullYear();

    let cell = `
      <div onclick="showDayPosts('${dateStr}')" 
           class="h-24 border border-gray-200 rounded-2xl p-2 hover:border-emerald-300 cursor-pointer transition ${isToday ? 'bg-emerald-50 border-emerald-300' : ''}">
        <div class="font-medium ${isToday ? 'text-emerald-600' : ''}">${day}</div>
    `;

    if (postsOnDay.length > 0) {
      cell += `<div class="text-[10px] text-emerald-600 mt-1">• ${postsOnDay.length} постов</div>`;
    }

    cell += `</div>`;
    grid.innerHTML += cell;
  }
}

function prevMonth() {
  calendarMonth--;
  if (calendarMonth < 0) {
    calendarMonth = 11;
    calendarYear--;
  }
  document.getElementById('calendarTitle').textContent = 
    new Date(calendarYear, calendarMonth).toLocaleString('ru-RU', { month: 'long', year: 'numeric' });
  renderCalendarGrid(calendarMonth, calendarYear);
}

function nextMonth() {
  calendarMonth++;
  if (calendarMonth > 11) {
    calendarMonth = 0;
    calendarYear++;
  }
  document.getElementById('calendarTitle').textContent = 
    new Date(calendarYear, calendarMonth).toLocaleString('ru-RU', { month: 'long', year: 'numeric' });
  renderCalendarGrid(calendarMonth, calendarYear);
}

function showDayPosts(dateStr) {
  const dayPosts = posts.filter(p => p.scheduledDate.startsWith(dateStr));
  
  if (dayPosts.length === 0) {
    alert(`На ${dateStr} нет запланированных публикаций`);
    return;
  }

  let text = `Публикации на ${dateStr}:\n\n`;
  dayPosts.forEach((p, i) => {
    text += `${i+1}. ${p.title} (${p.status})\n`;
  });

  alert(text);
}

function renderTags() {
  const main = document.getElementById('mainContent');

  // Собираем все уникальные теги
  const allTags = new Set();
  posts.forEach(post => {
    post.tags.forEach(tag => allTags.add(tag));
  });
    document.getElementById('rec_header').innerHTML = `<h1 class="text-2xl font-semibold text-gray-900" id="rec_header">Управление тегами</h1>`;
  let html = `
    <div class="bg-white rounded-3xl p-8">
      <div class="flex gap-3 mb-8">
        <input id="newTagInput" type="text" placeholder="Новый тег" 
               class="flex-1 px-5 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:border-emerald-500">
        <button onclick="addNewTag()" 
                class="bg-emerald-600 text-white px-8 rounded-2xl hover:bg-emerald-700">
          Добавить тег
        </button>
      </div>

      <div class="flex flex-wrap gap-3" id="tagsContainer">
        ${Array.from(allTags).map(tag => `
          <div class="group bg-gray-100 hover:bg-gray-200 transition px-5 py-2.5 rounded-2xl flex items-center gap-2">
            <span class="font-medium">#${tag}</span>
            <span onclick="deleteTag('${tag}'); event.stopImmediatePropagation()" 
                  class="hidden group-hover:inline text-red-500 cursor-pointer text-lg leading-none">×</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  main.innerHTML = html;
}

function addNewTag() {
  const input = document.getElementById('newTagInput');
  const tag = input.value.trim().toLowerCase();
  
  if (!tag) return;

  // Можно добавить логику сохранения популярных тегов, если нужно
  alert(`Тег "#${tag}" добавлен! Теперь его можно использовать при создании постов.`);
  input.value = '';
  renderTags(); // обновляем список
}

function deleteTag(tag) {
  if (confirm(`Удалить тег "#${tag}"?`)) {
    // Здесь можно добавить логику удаления тега из всех постов при необходимости
    renderTags();
  }
}

// Переключение страниц
function loadPage(page) {
  document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
  
  if (page === 'dashboard') renderDashboard();
  else if (page === 'posts') renderPosts();
  else if (page === 'new-post') renderNewPost();
  else if (page === 'moderation') renderModeration();
  else if (page === 'calendar') renderCalendar();
  else if (page === 'tags') renderTags();
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  if (checkAuth()) {
    renderSidebar();
    loadPage('dashboard');
    document.getElementById("name").innerHTML = `<div class="text-sm font-medium" id="name">${currentUser.name}</div>`
  }
});