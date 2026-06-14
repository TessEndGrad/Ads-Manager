<div align="center">

# 📢 Ads-Manager

### Платформа для планирования рекламных кампаний


</div>

***

## 📋 О проекте

**Ads-Manager** — это платформа для удобного планирования, управления и отслеживания рекламных кампаний. Проект предоставляет инструменты для организации рекламного процесса от идеи до запуска, включая интеграцию с Telegram для автоматической публикации постов.

***

## 🗂️ Структура проекта

```
Ads-Manager/
├── src/              # Backend (FastAPI)
├── bot/              # Telegram бот (aiogram)
├── web/              # Frontend (HTML/CSS/JS)
├── docker-compose.yml # Конфигурация Docker
├── requirements.txt  # Python зависимости
├── CONTRIBUTING.md   # Руководство для контрибьюторов
└── README.md         # Документация проекта
```

***

## 🚀 Быстрый старт

### Требования

- Docker
- Docker Compose
- Git

### Установка и запуск

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/TessEndGrad/Ads-Manager.git

# 2. Перейдите в директорию проекта
cd Ads-Manager

# 3. Запустите все сервисы одной командой
docker-compose up -d --build
```

После запуска будут доступны:
- 🌐 **Веб-интерфейс**: http://localhost
- 🔧 **API**: http://localhost:8000
- 📱 **Telegram бот**: запущен автоматически

### Остановка проекта

```bash
docker-compose down
```

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f api
docker-compose logs -f bot
docker-compose logs -f web
```

***

## ⚙️ Конфигурация

### Переменные окружения

Перед первым запуском создайте файл `.env` в корне проекта или настройте переменные в `docker-compose.yml`:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=rootroot
POSTGRES_DB=adsmanager

# API
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Telegram Bot
BOT_TOKEN=your-bot-token-here
BOT_API_EMAIL=bot@demo.ru
BOT_API_PASSWORD=123456
```

### Telegram бот

Для работы бота необходимо:
1. Создать бота через [@BotFather](https://t.me/BotFather)
2. Получить токен и добавить его в `BOT_TOKEN`
3. Создать технического пользователя в БД (автоматически через `seed_db.py`)

***

## ✨ Возможности

- 📅 **Планирование кампаний** — создавайте и управляйте рекламными кампаниями
- 🤖 **Telegram интеграция** — автоматическая публикация постов в каналы
- 📊 **Аналитика** — отслеживайте эффективность размещений
- 🗃️ **Организация** — структурируйте кампании по категориям и меткам
- 👥 **Ролевая модель** — разграничение прав пользователей и менеджеров
- 🔄 **Модерация** — система одобрения контента перед публикацией
- 📱 **Telegram бот** — создание и управление постами через мессенджер
- 🌐 **Веб-интерфейс** — удобная работа через браузер

***

## 🏗️ Архитектура

Проект состоит из следующих сервисов:

- **API** (FastAPI) — основной backend сервис
- **Web** (Nginx) — раздача frontend и проксирование API
- **Bot** (aiogram) — Telegram бот для управления постами
- **Database** (PostgreSQL) — хранилище данных

Все сервисы запускаются через Docker Compose и взаимодействуют через внутреннюю сеть.

***

## 🧪 Тестовые данные

Для заполнения базы тестовыми данными:

```bash
docker-compose exec api python -m src.scripts.seed_db
```

Будут созданы:
- Роли: `manager`, `user`
- Статусы постов: `draft`, `moderation`, `approved`, `published`, `rejected`
- Тестовые пользователи:
  - `manager@demo.ru` / `123456` (менеджер)
  - `user@demo.ru` / `123456` (пользователь)
  - `bot@demo.ru` / `123456` (технический пользователь для бота)

***

## 🤝 Вклад в проект

Мы рады любому вкладу! Пожалуйста, ознакомьтесь с [руководством для контрибьюторов](CONTRIBUTING.md) перед тем, как создавать pull request.

1. Сделайте форк репозитория
2. Создайте ветку для вашей фичи (`git checkout -b feature/my-feature`)
3. Зафиксируйте изменения (`git commit -m 'feat: добавить новую функцию'`)
4. Запушьте в ветку (`git push origin feature/my-feature`)
5. Откройте Pull Request

***

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).

***

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:
- Создайте [Issue](https://github.com/TessEndGrad/Ads-Manager/issues)
- Проверьте существующие обсуждения

***

<div align="center">

Сделано с ❤️ командой **TessEndGrad**

</div>
