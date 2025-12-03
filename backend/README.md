# Hotel Management Backend

Backend API для системи управління готелем, побудований на FastAPI з SQLite.

## Технології

- Python 3.11+
- FastAPI - веб-фреймворк
- SQLite - легка файлова база даних (не потребує окремого сервера)
- SQLAlchemy - ORM
- Alembic - міграції БД
- JWT - авторизація
- Bcrypt - хешування паролів
- Poetry - управління залежностями

## Встановлення

### 1. Встановіть Poetry

```bash
pip install poetry
```

### 2. Встановіть залежності

```bash
cd backend
poetry install
```

### 3. Налаштуйте змінні середовища

Скопіюйте `.env.example` в `.env` та заповніть своїми даними:

```bash
cp .env.example .env
```

Приклад `.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///./hotel.db
SECRET_KEY=your-very-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Примітка:** База даних SQLite створюється автоматично як файл `hotel.db` в корені папки backend при першому запуску міграцій.

### 4. Запустіть міграції

```bash
poetry run alembic upgrade head
```

Це створить файл `hotel.db` з усіма необхідними таблицями.

### 5. Створіть початкового адміністратора (опціонально)

Ви можете створити користувача через API або вручну через SQLite:

```sql
INSERT INTO users (email, username, hashed_password, role, is_active)
VALUES (
    'admin@hotel.com',
    'admin',
    '$2b$12$...',  -- захешований пароль
    'admin',
    true
);
```

## Запуск

### Режим розробки

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Продакшн

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Сервер буде доступний за адресою: http://localhost:8000

API документація (Swagger): http://localhost:8000/docs

## Архітектура

Проект використовує MVC (Model-View-Controller) архітектуру:

```
app/
├── models/          # Моделі бази даних (SQLAlchemy)
├── controllers/     # Бізнес-логіка
├── views/           # API endpoints (роути)
├── schemas/         # Pydantic схеми для валідації
├── repositories/    # Доступ до БД через паттерн Repository
├── dependencies/    # Dependency Injection
├── core/            # Конфігурація, безпека
└── database/        # Підключення до БД
```

## API Endpoints

### Авторизація

- `POST /api/auth/register` - Реєстрація нового користувача
- `POST /api/auth/login` - Вхід в систему (отримання JWT токена)

### Користувачі

- `GET /api/users/me` - Отримати інформацію про поточного користувача
- `GET /api/users` - Список всіх користувачів (тільки менеджер)
- `GET /api/users/{id}` - Деталі користувача (тільки менеджер)
- `PUT /api/users/{id}` - Оновити користувача (тільки менеджер)
- `DELETE /api/users/{id}` - Видалити користувача (тільки менеджер)

### Номери

- `GET /api/rooms` - Список всіх номерів (з фільтрами)
- `GET /api/rooms/{id}` - Деталі номера
- `POST /api/rooms` - Створити номер (тільки менеджер)
- `PUT /api/rooms/{id}` - Оновити номер (тільки менеджер)
- `DELETE /api/rooms/{id}` - Видалити номер (тільки менеджер)

### Бронювання

- `GET /api/bookings/my` - Мої бронювання
- `GET /api/bookings/all` - Всі бронювання (тільки менеджер)
- `GET /api/bookings/{id}` - Деталі бронювання
- `POST /api/bookings` - Створити бронювання
- `PUT /api/bookings/{id}` - Оновити бронювання
- `POST /api/bookings/{id}/cancel` - Скасувати бронювання
- `DELETE /api/bookings/{id}` - Видалити бронювання (тільки менеджер)

## Ролі користувачів

- **user** - звичайний користувач (може переглядати номери та створювати бронювання)
- **manager** - менеджер готелю (повний доступ до CRUD операцій)
- **admin** - системний адміністратор (повний доступ)

## Міграції бази даних

### Створити нову міграцію

```bash
poetry run alembic revision --autogenerate -m "description"
```

### Застосувати міграції

```bash
poetry run alembic upgrade head
```

### Відкотити міграцію

```bash
poetry run alembic downgrade -1
```

## Тестування

```bash
poetry run pytest
```

## Безпека

- Паролі хешуються за допомогою bcrypt
- JWT токени для авторизації
- Role-Based Access Control (RBAC)
- Dependency Injection для керування залежностями
- Валідація всіх вхідних даних через Pydantic

## Troubleshooting

### Помилка підключення до бази даних

Переконайтеся, що DATABASE_URL правильно налаштований в `.env`:
```env
DATABASE_URL=sqlite+aiosqlite:///./hotel.db
```

База даних SQLite створюється автоматично, тому проблеми з підключенням зустрічаються рідко.

### Помилка при міграціях

Переконайтеся, що у вас є права на запис файлів в папці backend.

```bash
poetry run alembic current  # Перевірити поточну версію
poetry run alembic history  # Показати історію міграцій
```

### Видалення бази даних

Якщо потрібно почати з чистої бази:

```bash
# Видаліть файл бази даних
rm hotel.db

# Створіть нову базу з міграціями
poetry run alembic upgrade head
```
