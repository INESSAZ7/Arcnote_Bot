# 📚 Arcnote_Bot

Telegram-бот для сохранения, категоризации и напоминания о полезных ссылках (статьи, видео, ресурсы) с поддержкой полнотекстового поиска и мультиязычной обработки.

---

## ⚙️ Функциональность

- ✅ Сохранение ссылок с указанием тематики и подкатегории
- ✅ Определение языка статьи
- ✅ Автоматическое извлечение заголовка и описания
- ✅ Поддержка YouTube, GitHub, Habr, Medium и др.
- ✅ Напоминания с возможностью отложить
- ✅ Полнотекстовый поиск по summary
- ✅ Фильтрация по темам и статусу прочитанности

---

## 🧩 Архитектура

- **Язык**: Python 3.10+
- **Фреймворк бота**: `aiogram`
- **База данных**: PostgreSQL
- **Планировщик**: `apscheduler`
- **Доп. библиотеки**:
  - `newspaper3k` — извлечение описания статьи
  - `langdetect` — определение языка
  - `asyncpg` — PostgreSQL драйвер
  - `psycopg2` — для CLI и миграций

---

## 📂 Структура проекта

project/
│
├── bot.py # Точка входа
├── handlers/
│ ├── add_link.py # Добавление ссылки
│ ├── search.py # Поиск по summary
│ ├── reminders.py # Управление напоминаниями
│ └── list_links.py # Просмотр сохранённого
│
├── services/
│ ├── link_parser.py # Определение типа ресурса
│ ├── summarizer.py # Парсинг заголовка и текста
│ ├── language.py # Определение языка текста
│ └── scheduler.py # Планирование уведомлений
│
├── db/
│ ├── connection.py # Работа с БД
│ └── queries.py # SQL-запросы
│
├── schema.sql # Структура таблиц
├── README.md
└── requirements.txt


---

## 🗃️ Структура базы данных

### 📄 `users`

| Поле         | Тип        | Описание           |
|--------------|------------|--------------------|
| id           | SERIAL     | PK                 |
| telegram_id  | BIGINT     | Telegram ID        |
| username     | TEXT       | Логин              |
| first_name   | TEXT       | Имя                |
| last_name    | TEXT       | Фамилия            |
| created_at   | TIMESTAMP  | Дата регистрации   |

---

### 📄 `links`

| Поле          | Тип         | Описание                          |
|---------------|-------------|-----------------------------------|
| id            | SERIAL      | PK                                |
| user_id       | INTEGER     | FK → users(id)                    |
| url           | TEXT        | Ссылка                            |
| title         | TEXT        | Заголовок                         |
| topic         | TEXT        | Тематика (например: аналитика)    |
| subcategory   | TEXT        | Подкатегория (например: A/B)      |
| summary       | TEXT        | Краткое описание                  |
| resource_type | TEXT / ENUM | Тип ресурса (youtube, article…)   |
| lang          | VARCHAR(10) | Язык текста ('ru', 'en', ...)     |
| tsv_summary   | TSVECTOR    | Индекс полнотекстового поиска     |
| created_at    | TIMESTAMP   | Дата добавления                   |

---

### 📄 `reminders`

| Поле       | Тип        | Описание                          |
|------------|------------|-----------------------------------|
| id         | SERIAL     | PK                                |
| link_id    | INTEGER    | FK → links(id)                    |
| remind_at  | TIMESTAMP  | Время напоминания                 |
| sent       | BOOLEAN    | Было ли отправлено                |
| created_at | TIMESTAMP  | Когда создано                     |

---

## 📥 Команды бота

### `/start`
Регистрация нового пользователя.

---

### `/add <url> [тематика] [подкатегория]`
Добавление новой ссылки, автоматический парсинг и планирование напоминания.

Пример:
/add https://habr.com/post/abc аналитика AB


---

### `/list [тематика]`
Список ссылок (по тематикам и подкатегориям).

Пример:
/list аналитика


---

### `/remind`
Настройка или отложить напоминание о ссылке.

---

### `/search <запрос>`
Полнотекстовый поиск по кратким описаниям с учётом языка.

---

## 🧠 Интеллектуальные функции

| Возможность                   | Детали                                |
|------------------------------|----------------------------------------|
| Определение языка текста     | `langdetect`                           |
| Автогенерация описания       | `newspaper3k`                          |
| Категоризация                | тема / подкатегория                   |
| Поиск                        | PostgreSQL `tsvector + GIN index`     |
| Типы ресурсов                | YouTube / GitHub / Article / Other    |

---

## 🔧 Установка

```bash
git clone https://github.com/yourname/link-bot.git
cd link-bot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
psql -U postgres -d yourdb -f schema.sql

python bot.py
```