let currentUser = null;

const users = [
  { id: 1, email: "moderator@demo.ru", password: "123456", name: "Модератор", role: "moderator" },
  { id: 2, email: "user@demo.ru", password: "123456", name: "Алексей Иванов", role: "user" }
];

let posts = [
  {
    id: 1,
    title: "Как увеличить продажи через Telegram в 2026",
    text: "Подробный гайд...",
    media: ["https://picsum.photos/800/600"],
    tags: ["продажи", "telegram"],
    scheduledDate: "2026-05-12T14:00",
    status: "published",
    authorId: 2,
    createdAt: "2026-05-01"
  },
  {
    id: 2,
    title: "Новый тариф для корпоративных клиентов",
    text: "Отличное предложение...",
    media: [],
    tags: ["новость", "продажи"],
    scheduledDate: "2026-05-15T10:00",
    status: "moderation",
    authorId: 2,
    createdAt: "2026-05-07"
  }
];

function saveData() {
  localStorage.setItem('posts', JSON.stringify(posts));
  localStorage.setItem('currentUser', JSON.stringify(currentUser));
}