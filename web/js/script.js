const API = '/api/v1';

let currentUser = null;
let posts = [];
let currentFilter = { status: 'all', tag: 'all', sort: 'date-desc' };
let calendarMonth = new Date().getMonth();
let calendarYear = new Date().getFullYear();

// ─── AUTH HELPERS ────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

async function fetchCurrentUser() {
  const res = await fetch(`${API}/users/me`, { headers: authHeaders() });
  if (res.status === 401) { logout(); return null; }
  return await res.json();
}

function checkAuth() {
  const token = getToken();
  const currentPage = window.location.pathname.split('/').pop();
  if (!token) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = 'login.html';
}

// ─── API CALLS ───────────────────────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  const token = getToken();
  // Убираем двойной слэш: нормализуем путь
  const url = `${API}/${path}`.replace(/\/+/g, '/');
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (res.status === 401) { logout(); return null; }
  return res;
}

async function loadPosts(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status && filters.status !== 'all') params.set('status_id', filters.status);
  if (filters.tag_ids && filters.tag_ids.length) filters.tag_ids.forEach(id => params.append('tag_ids', id));
  if (filters.scheduled_from) params.set('scheduled_from', filters.scheduled_from);
  if (filters.scheduled_to) params.set('scheduled_to', filters.scheduled_to);
  if (filters.order_by) params.set('order_by', filters.order_by);
  if (filters.order_dir) params.set('order_dir', filters.order_dir);
  params.set('page_size', '100');

  const res = await apiFetch(`/posts/?${params}`);
  if (!res || !res.ok) return [];
  const data = await res.json();
  return data.items || [];
}

async function loadTags() {
  const res = await apiFetch('/tags/');
  if (!res || !res.ok) return [];
  return await res.json();
}

// ─── SIDEBAR ─────────────────────────────────────────────────────────────────

function renderSidebar() {
  const menu = document.getElementById('sidebarMenu');
  const isManager = currentUser?.role?.name === 'manager';

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
    ${isManager ? `
    <div onclick="loadPage('moderation')" class="menu-item flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer">
      <i class="fas fa-user-shield w-5"></i><span>Модерация</span>
    </div>` : ''}
  `;
}

// ─── DASHBOARD ───────────────────────────────────────────────────────────────

async function renderDashboard() {
  document.getElementById('rec_header').innerHTML =
    `<h1 class="text-2xl font-semibold text-gray-900">Добро пожаловать, ${currentUser.username}!</h1>`;

  const main = document.getElementById('mainContent');
  main.innerHTML = `<p class="text-gray-400">Загрузка...</p>`;

  posts = await loadPosts();

  const onModeration = posts.filter(p => p.status_id === 2).length;
  const published    = posts.filter(p => p.status_id === 4).length;

  main.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-3xl shadow-sm">
        <h3 class="text-gray-500">Всего публикаций</h3>
        <p class="text-5xl font-semibold mt-2">${posts.length}</p>
      </div>
      <div class="bg-white p-6 rounded-3xl shadow-sm">
        <h3 class="text-gray-500">Ожидают модерации</h3>
        <p class="text-5xl font-semibold mt-2 text-amber-600">${onModeration}</p>
      </div>
      <div class="bg-white p-6 rounded-3xl shadow-sm">
        <h3 class="text-gray-500">Опубликовано</h3>
        <p class="text-5xl font-semibold mt-2 text-emerald-600">${published}</p>
      </div>
    </div>
  `;
}

// ─── POSTS LIST ──────────────────────────────────────────────────────────────

const STATUS_LABELS = {
  1: { label: 'Черновик',       cls: 'bg-gray-100 text-gray-600' },
  2: { label: 'На модерации',   cls: 'bg-amber-100 text-amber-700' },
  3: { label: 'Одобрен',        cls: 'bg-blue-100 text-blue-700' },
  4: { label: 'Опубликован',    cls: 'bg-emerald-100 text-emerald-700' },
  5: { label: 'Отклонён',       cls: 'bg-red-100 text-red-600' },
};

async function renderPosts() {
  document.getElementById('rec_header').innerHTML =
    `<h1 class="text-2xl font-semibold text-gray-900">Рекламные кампании</h1>`;

  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="flex flex-wrap gap-3 mb-6">
      <select id="filterStatus" onchange="applyFilter()" class="px-4 py-2 border border-gray-200 rounded-2xl text-sm">
        <option value="all">Все статусы</option>
        <option value="1">Черновик</option>
        <option value="2">На модерации</option>
        <option value="3">Одобрен</option>
        <option value="4">Опубликован</option>
        <option value="5">Отклонён</option>
      </select>
      <select id="filterSort" onchange="applyFilter()" class="px-4 py-2 border border-gray-200 rounded-2xl text-sm">
        <option value="created_at|desc">Сначала новые</option>
        <option value="created_at|asc">Сначала старые</option>
        <option value="scheduled_at|asc">По дате публикации ↑</option>
        <option value="scheduled_at|desc">По дате публикации ↓</option>
        <option value="title|asc">По названию А-Я</option>
      </select>
      <input id="filterSearch" type="text" placeholder="Поиск..."
             oninput="applyFilter()"
             class="px-4 py-2 border border-gray-200 rounded-2xl text-sm flex-1 min-w-[200px]">
    </div>
    <div id="postsList"><p class="text-gray-400">Загрузка...</p></div>
  `;

  await applyFilter();
}

async function applyFilter() {
  const status  = document.getElementById('filterStatus')?.value || 'all';
  const sortVal = document.getElementById('filterSort')?.value   || 'created_at|desc';
  const search  = document.getElementById('filterSearch')?.value || '';
  const [order_by, order_dir] = sortVal.split('|');

  const filters = { order_by, order_dir };
  if (status !== 'all') filters.status = status;

  let items = await loadPosts(filters);

  if (search) {
    const q = search.toLowerCase();
    items = items.filter(p =>
      (p.title   || '').toLowerCase().includes(q) ||
      (p.content || '').toLowerCase().includes(q)
    );
  }

  posts = items;
  renderPostsList(items);
}

function renderPostsList(items) {
  const container = document.getElementById('postsList');
  if (!container) return;

  if (!items.length) {
    container.innerHTML = `<p class="text-gray-400 mt-8 text-center">Публикации не найдены</p>`;
    return;
  }

  container.innerHTML = items.map(post => {
    const s = STATUS_LABELS[post.status_id] || { label: '—', cls: 'bg-gray-100 text-gray-500' };
    const tags = (post.tags || []).map(t =>
      `<span class="text-xs bg-gray-100 px-3 py-1 rounded-full">#${t.name}</span>`
    ).join('');
    const date = post.scheduled_at
      ? new Date(post.scheduled_at).toLocaleString('ru-RU') : '—';

    return `
      <div class="pub-card bg-white rounded-3xl p-6 shadow-sm cursor-pointer hover:shadow-md mb-4"
           onclick="viewPost(${post.id})">
        <div class="flex justify-between items-start">
          <h3 class="font-semibold text-lg leading-tight">${post.title || 'Без названия'}</h3>
          <span class="text-xs px-3 py-1 rounded-full ${s.cls}">${s.label}</span>
        </div>
        <p class="text-gray-500 text-sm mt-4 line-clamp-2">
          ${(post.content || '').substring(0, 120)}${(post.content || '').length > 120 ? '...' : ''}
        </p>
        <div class="flex flex-wrap gap-2 mt-4">${tags}</div>
        <div class="text-xs text-gray-400 mt-4">${date}</div>
      </div>
    `;
  }).join('');
}

// ─── VIEW POST ────────────────────────────────────────────────────────────────

async function viewPost(id) {
  const res = await apiFetch(`/posts/${id}`);
  if (!res || !res.ok) { alert('Не удалось загрузить пост'); return; }
  const post = await res.json();

  const main = document.getElementById('mainContent');
  const s = STATUS_LABELS[post.status_id] || { label: '—', cls: 'bg-gray-100' };
  const isManager = currentUser?.role?.name === 'manager';

  const mediaHtml = (post.media || []).map(m =>
    m.media_type?.startsWith('video')
      ? `<video src="${m.file_url}" controls class="w-full rounded-2xl mt-6"></video>`
      : `<img src="${m.file_url}" class="w-full rounded-2xl mt-6" alt="">`
  ).join('');

  const tags = (post.tags || []).map(t =>
    `<span class="text-sm bg-gray-100 px-3 py-1 rounded-full">#${t.name}</span>`
  ).join('');

  const moderationBtns = isManager && post.status_id === 2 ? `
    <button onclick="approvePost(${post.id})"
            class="flex-1 bg-emerald-600 text-white py-4 rounded-2xl font-medium hover:bg-emerald-700">
      Одобрить и опубликовать
    </button>
    <button onclick="rejectPost(${post.id})"
            class="flex-1 border border-red-300 text-red-600 py-4 rounded-2xl font-medium hover:bg-red-50">
      Отклонить
    </button>
  ` : '';

  main.innerHTML = `
    <button onclick="loadPage('posts')"
            class="mb-6 text-emerald-600 hover:underline flex items-center gap-2">
      ← Назад к списку
    </button>
    <div class="bg-white rounded-3xl p-10 max-w-4xl mx-auto">
      <div class="flex justify-between items-start mb-4">
        <h1 class="text-3xl font-semibold">${post.title || 'Без названия'}</h1>
        <span class="text-sm px-4 py-1 rounded-full ${s.cls}">${s.label}</span>
      </div>
      <p class="text-gray-500">
        ${post.scheduled_at ? new Date(post.scheduled_at).toLocaleString('ru-RU') : '—'}
      </p>
      ${mediaHtml}
      <div class="prose mt-8 text-gray-700 leading-relaxed">${post.content || ''}</div>
      <div class="flex flex-wrap gap-2 mt-6">${tags}</div>
      <div class="mt-10 flex gap-4">${moderationBtns}</div>
    </div>
  `;
}

// ─── CREATE POST ──────────────────────────────────────────────────────────────

async function renderNewPost() {
  const modal = document.getElementById('card-modal');
  const body  = document.getElementById('modal-body');

  const tagsData = await loadTags();
  const tagOptions = tagsData.map(t =>
    `<label class="flex items-center gap-2 cursor-pointer">
       <input type="checkbox" value="${t.id}" class="post-tag-cb rounded"> #${t.name}
     </label>`
  ).join('');

  body.innerHTML = `
    <h1 class="text-3xl font-semibold mb-8">Новая публикация</h1>
    <div class="max-w-2xl bg-white rounded-3xl p-10">
      <input id="postTitle" type="text" placeholder="Заголовок публикации"
             class="w-full px-5 py-4 border border-gray-300 rounded-2xl text-lg mb-6">
      <textarea id="postText" rows="6" placeholder="Текст публикации..."
                class="w-full px-5 py-4 border border-gray-300 rounded-2xl mb-6"></textarea>
      <input id="postDate" type="datetime-local"
             class="w-full px-5 py-4 border border-gray-300 rounded-2xl mb-6">
      ${tagOptions ? `
        <div class="mb-6">
          <p class="text-sm text-gray-500 mb-3">Теги:</p>
          <div class="flex flex-wrap gap-4">${tagOptions}</div>
        </div>` : ''}
      <div id="createPostError" class="text-red-500 text-sm mb-4 hidden"></div>
      <button onclick="createPost()"
              class="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-4 rounded-2xl text-lg font-medium">
        Создать публикацию
      </button>
    </div>
  `;
  modal.style.display = 'flex';
}

function closeModal() {
  document.getElementById('card-modal').style.display = 'none';
}

async function createPost() {
  const title      = document.getElementById('postTitle').value.trim();
  const content    = document.getElementById('postText').value.trim();
  const scheduledAt = document.getElementById('postDate').value;
  const tagIds     = Array.from(document.querySelectorAll('.post-tag-cb:checked'))
                          .map(cb => parseInt(cb.value));

  const errEl = document.getElementById('createPostError');
  if (!title || !content) {
    errEl.textContent = 'Заполните заголовок и текст';
    errEl.classList.remove('hidden');
    return;
  }
  errEl.classList.add('hidden');

  const bodyData = { title, content, tag_ids: tagIds };
  if (scheduledAt) bodyData.scheduled_at = new Date(scheduledAt).toISOString();

  const res = await apiFetch('/posts/', {
    method: 'POST',
    body: JSON.stringify(bodyData)
  });

  if (res && res.ok) {
    closeModal();
    alert('Публикация создана!');
    loadPage('posts');
  } else {
    const err = res ? await res.json() : null;
    errEl.textContent = err?.detail || 'Ошибка при создании';
    errEl.classList.remove('hidden');
  }
}

// ─── MODERATION ───────────────────────────────────────────────────────────────

async function renderModeration() {
  const isManager = currentUser?.role?.name === 'manager';
  if (!isManager) { alert('Доступ запрещён'); return; }

  document.getElementById('rec_header').innerHTML =
    `<h1 class="text-2xl font-semibold text-gray-900">Модерация публикаций</h1>`;

  const main = document.getElementById('mainContent');
  main.innerHTML = `<p class="text-gray-400">Загрузка...</p>`;

  const items = await loadPosts({ status: 2 });

  if (!items.length) {
    main.innerHTML = `<p class="text-gray-500 mt-8 text-center">Нет публикаций на модерации</p>`;
    return;
  }

  main.innerHTML = items.map(post => `
    <div id="mod-${post.id}" class="bg-white p-6 rounded-3xl mb-6 shadow-sm">
      <h3 class="font-semibold text-lg">${post.title || 'Без названия'}</h3>
      <p class="text-sm text-gray-500 mt-2">${(post.content || '').substring(0, 150)}...</p>
      <p class="text-xs text-gray-400 mt-2">
        ${post.scheduled_at ? new Date(post.scheduled_at).toLocaleString('ru-RU') : ''}
      </p>
      <div class="mt-6 flex gap-4">
        <button onclick="approvePost(${post.id})"
                class="px-6 py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700">
          Одобрить
        </button>
        <button onclick="rejectPost(${post.id})"
                class="px-6 py-3 border border-red-300 text-red-600 rounded-2xl hover:bg-red-50">
          Отклонить
        </button>
      </div>
    </div>
  `).join('');
}

async function approvePost(id) {
  const res = await apiFetch(`/posts/${id}/approve`, { method: 'POST' });
  if (res && res.ok) {
    document.getElementById(`mod-${id}`)?.remove();
    alert('Публикация одобрена!');
  } else {
    alert('Ошибка при одобрении');
  }
}

async function rejectPost(id) {
  if (!confirm('Отклонить публикацию?')) return;
  const res = await apiFetch(`/posts/${id}/reject`, { method: 'POST' });
  if (res && res.ok) {
    document.getElementById(`mod-${id}`)?.remove();
    alert('Публикация отклонена');
  } else {
    alert('Ошибка при отклонении');
  }
}

// ─── CALENDAR ─────────────────────────────────────────────────────────────────

async function renderCalendar() {
  document.getElementById('rec_header').innerHTML =
    `<h1 class="text-2xl font-semibold text-gray-900">Календарь публикаций</h1>`;

  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="bg-white rounded-3xl p-8 shadow-sm">
      <div class="flex justify-between items-center mb-6">
        <button onclick="prevMonth()" class="text-2xl px-4 py-2 hover:bg-gray-100 rounded-xl">‹</button>
        <h2 id="calendarTitle" class="text-2xl font-medium"></h2>
        <button onclick="nextMonth()" class="text-2xl px-4 py-2 hover:bg-gray-100 rounded-xl">›</button>
      </div>
      <div class="grid grid-cols-7 gap-2 text-center text-sm font-medium text-gray-500 mb-2">
        <div>Пн</div><div>Вт</div><div>Ср</div><div>Чт</div><div>Пт</div><div>Сб</div><div>Вс</div>
      </div>
      <div id="calendarGrid" class="grid grid-cols-7 gap-2"></div>
    </div>
  `;

  posts = await loadPosts();
  renderCalendarGrid(calendarMonth, calendarYear);
}

function renderCalendarGrid(month, year) {
  const titleEl = document.getElementById('calendarTitle');
  if (titleEl) titleEl.textContent =
    new Date(year, month).toLocaleString('ru-RU', { month: 'long', year: 'numeric' });

  const grid = document.getElementById('calendarGrid');
  if (!grid) return;
  grid.innerHTML = '';

  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
    grid.innerHTML += `<div class="h-24"></div>`;
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr    = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const postsOnDay = posts.filter(p => p.scheduled_at?.startsWith(dateStr));
    const isToday    = day === new Date().getDate() &&
                       month === new Date().getMonth() &&
                       year  === new Date().getFullYear();

    grid.innerHTML += `
      <div onclick="showDayPosts('${dateStr}')"
           class="h-24 border border-gray-200 rounded-2xl p-2 hover:border-emerald-300 cursor-pointer transition
                  ${isToday ? 'bg-emerald-50 border-emerald-300' : ''}">
        <div class="font-medium ${isToday ? 'text-emerald-600' : ''}">${day}</div>
        ${postsOnDay.length
          ? `<div class="text-[10px] text-emerald-600 mt-1">• ${postsOnDay.length} пост(ов)</div>`
          : ''}
      </div>
    `;
  }
}

function prevMonth() {
  calendarMonth--;
  if (calendarMonth < 0) { calendarMonth = 11; calendarYear--; }
  renderCalendarGrid(calendarMonth, calendarYear);
}

function nextMonth() {
  calendarMonth++;
  if (calendarMonth > 11) { calendarMonth = 0; calendarYear++; }
  renderCalendarGrid(calendarMonth, calendarYear);
}

function showDayPosts(dateStr) {
  const dayPosts = posts.filter(p => p.scheduled_at?.startsWith(dateStr));
  if (!dayPosts.length) { alert(`На ${dateStr} нет запланированных публикаций`); return; }
  alert(`Публикации на ${dateStr}:\n\n` +
    dayPosts.map((p, i) =>
      `${i + 1}. ${p.title} (${STATUS_LABELS[p.status_id]?.label || '—'})`
    ).join('\n')
  );
}

// ─── TAGS ─────────────────────────────────────────────────────────────────────

async function renderTags() {
  document.getElementById('rec_header').innerHTML =
    `<h1 class="text-2xl font-semibold text-gray-900">Управление тегами</h1>`;

  const main = document.getElementById('mainContent');
  main.innerHTML = `<p class="text-gray-400">Загрузка...</p>`;

  const tags = await loadTags();

  main.innerHTML = `
    <div class="bg-white rounded-3xl p-8">
      <div class="flex gap-3 mb-8">
        <input id="newTagInput" type="text" placeholder="Новый тег"
               class="flex-1 px-5 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:border-emerald-500">
        <button onclick="addNewTag()"
                class="bg-emerald-600 text-white px-8 rounded-2xl hover:bg-emerald-700">
          Добавить
        </button>
      </div>
      <div class="flex flex-wrap gap-3" id="tagsContainer">
        ${tags.length
          ? tags.map(tag => `
              <div class="group bg-gray-100 hover:bg-gray-200 transition px-5 py-2.5 rounded-2xl flex items-center gap-2">
                <span class="font-medium">#${tag.name}</span>
                <span onclick="deleteTag(${tag.id}, '${tag.name}')"
                      class="hidden group-hover:inline text-red-500 cursor-pointer text-lg leading-none">×</span>
              </div>`).join('')
          : '<p class="text-gray-400">Теги не найдены</p>'}
      </div>
    </div>
  `;
}

async function addNewTag() {
  const input = document.getElementById('newTagInput');
  const name  = input.value.trim().toLowerCase();
  if (!name) return;

  const res = await apiFetch('/tags/', {
    method: 'POST',
    body: JSON.stringify({ name })
  });

  if (res && res.ok) {
    input.value = '';
    renderTags();
  } else {
    const err = res ? await res.json() : null;
    alert(err?.detail || 'Ошибка при создании тега');
  }
}

async function deleteTag(id, name) {
  if (!confirm(`Удалить тег "#${name}"?`)) return;
  const res = await apiFetch(`/tags/${id}`, { method: 'DELETE' });
  if (res && (res.ok || res.status === 204)) {
    renderTags();
  } else {
    alert('Ошибка при удалении тега');
  }
}

// ─── NAVIGATION ───────────────────────────────────────────────────────────────

function loadPage(page) {
  document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
  if      (page === 'dashboard')  renderDashboard();
  else if (page === 'posts')      renderPosts();
  else if (page === 'new-post')   renderNewPost();
  else if (page === 'moderation') renderModeration();
  else if (page === 'calendar')   renderCalendar();
  else if (page === 'tags')       renderTags();
}

// ─── INIT ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  currentUser = await fetchCurrentUser();
  if (!currentUser) return;

  renderSidebar();
  loadPage('dashboard');

  const nameEl = document.getElementById('name');
  if (nameEl) nameEl.innerHTML =
    `<div class="text-sm font-medium">${currentUser.username}</div>`;
});
