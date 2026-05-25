# Adds-Manager
Платформа для планирования рекламных кампаний



# 📂 Структура проекта
adds-manager/                        
├── src/                              
│   │
│   ├── core/                         
│   │   ├── config.py                 # Конфигурация приложения
│   │   ├── database.py               # Настройка подключения к БД
│   │   ├── dependencies.py           # FastAPI зависимости 
│   │   ├── exceptions.py             # Базовые исключения приложения
│   │   ├── events/                   # Базовые классы для работы с Domain Events
│   │   ├── mediator.py               
│   │   ├── logging_config.py         # Настройка логирования
│   │   └── utils.py                  # Общие утилиты 
│   │
│   ├── modules/                      
│   │   ├── posts/                    # Модуль "Посты" 
│   │   ├── users/                    # Модуль "Пользователи" 
│   │   ├── campaigns/                # Модуль "Кампании" (группировка постов) 
│   │   ├── integrations/             # Модуль интеграций с внешними сервисами 
│   │   └── notifications/            # Модуль уведомлений (о согласовании, ошибках публикации и т.д.)
│   │
│   ├── application/                  
│   │   ├── event_handlers/           # Обработчики доменных событий 
│   │   └── interfaces/               # Интерфейсы Application Layer если понадобиться
│   │
│   ├── domain/                       
│   │   ├── entities/                 
│   │   ├── events/                   
│   │   └── value_objects/            
│   │
│   ├── infrastructure/               
│   │   ├── persistence/              
│   │   │   ├── models/               # SQLAlchemy ORM-модели 
│   │   │   ├── repositories/         # Конкретные реализации репозиториев
│   │   │   ├── mappings.py           # Маппинг между Domain Entities и ORM моделями
│   │   │   └── unit_of_work.py       # Управление транзакциями
│   │   │
│   │   └── integrations/             # Клиенты внешних API
│   │       ├── vk/
│   │       ├── telegram/
│   │       └── publishing_service.py # Сервис автопубликации постов
│   │   
│   │
│   ├── api/                          
│   │   ├── v1/                       
│   │   │   ├── routers/              # FastAPI роутеры 
│   │   │   ├── schemas/              # Pydantic-схемы 
│   │   │   └── dependencies.py       
│   │   └── main.py                   # Создание и конфигурация FastAPI приложения
│   │
│   ├── common/                       # Общие компоненты, не относящиеся строго к DDD-слоям
│   │   ├── exceptions.py             # Дополнительные исключения
│   │   ├── dto.py                    # Общие дтошки
│   │   └── decorators.py             # Декораторы 
│   │
│   └── main.py                       # Точка входа приложения, запускать будет фаст апи
│
├── tests/                            # Автоматизированные тесты
│   ├── unit/                         # Юнит-тесты 
│   ├── integration/                  # Интеграционные тесты 
│   └── e2e/                          # End-to-End тесты 
|
├── web/                              # Front-End
|   
|
│
├── scripts/                          
│   ├── seed_db.py                    # Заполнение базы тестовыми данными
│   └── create_superuser.py
│
├── docker-compose.yml                # Конфигурация Docker Compose
├── Dockerfile                        # Dockerfile для FastAPI приложения
├── requirements.txt                  # Зависимости проекта
├── .env.example                      # Пример файла окружения
├── .gitignore
└── README.md
