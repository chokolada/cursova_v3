# Інструкція по встановленню та запуску проекту

## Швидкий старт

### Вимоги

- Python 3.11+
- Node.js 16+
- Poetry

**Примітка:** PostgreSQL не потрібен! Проект використовує SQLite - легку файлову базу даних.

### Крок 1: Налаштування Backend

```bash
# Перейдіть в папку backend
cd backend

# Встановіть Poetry (якщо ще не встановлений)
pip install poetry

# Встановіть залежності
poetry install

# Створіть .env файл
cp .env.example .env

# Відредагуйте .env файл з вашими налаштуваннями
# DATABASE_URL=sqlite+aiosqlite:///./hotel.db
# SECRET_KEY=your-secret-key

# Запустіть міграції (база даних створюється автоматично)
poetry run alembic upgrade head

# Запустіть сервер
poetry run uvicorn app.main:app --reload
```

Backend буде доступний за адресою: http://localhost:8000

API документація: http://localhost:8000/docs

**Примітка:** Файл бази даних `hotel.db` буде створений автоматично в папці backend.

### Крок 2: Налаштування Frontend

```bash
# Відкрийте новий термінал
# Перейдіть в папку frontend
cd frontend

# Встановіть залежності
npm install

# Створіть .env файл (якщо потрібно)
# REACT_APP_API_URL=http://localhost:8000/api

# Запустіть сервер розробки
npm start
```

Frontend буде доступний за адресою: http://localhost:3000

### Крок 3: Створення тестових даних

#### Створення користувачів

1. Зареєструйте звичайного користувача через інтерфейс
2. Створіть менеджера через API або базу даних:

```bash
# Використайте API endpoint або вручну через SQLite
# Можна використати DB Browser for SQLite для редагування бази
```

Приклад реєстрації менеджера через API (POST /api/auth/register):

```json
{
  "username": "manager",
  "email": "manager@hotel.com",
  "password": "manager123",
  "role": "manager"
}
```

Примітка: За замовчуванням role при реєстрації через фронтенд завжди "user". Для створення менеджера потрібно використати прямий API запит або змінити role в базі даних.

#### Створення номерів

Увійдіть як менеджер та створіть номери через адміністративну панель:

1. Перейдіть в `/admin`
2. Заповніть форму створення номера
3. Створіть декілька різних номерів

Приклад номерів:

```json
{
  "room_number": "101",
  "room_type": "single",
  "price_per_night": 100.00,
  "capacity": 1,
  "description": "Комфортний одномісний номер",
  "amenities": "WiFi, TV, Кондиціонер",
  "floor": 1,
  "is_available": true
}

{
  "room_number": "201",
  "room_type": "double",
  "price_per_night": 150.00,
  "capacity": 2,
  "description": "Просторий двомісний номер",
  "amenities": "WiFi, TV, Кондиціонер, Міні-бар",
  "floor": 2,
  "is_available": true
}

{
  "room_number": "301",
  "room_type": "suite",
  "price_per_night": 300.00,
  "capacity": 4,
  "description": "Розкішний сьют з окремою вітальнею",
  "amenities": "WiFi, Smart TV, Кондиціонер, Міні-бар, Джакузі",
  "floor": 3,
  "is_available": true
}
```

## Тестування функціоналу

### Для звичайного користувача (user):

1. Зареєструйтеся на `/register`
2. Увійдіть на `/login`
3. Перегляньте список номерів на головній сторінці
4. Виберіть номер та натисніть "Book Now"
5. Заповніть форму бронювання
6. Перегляньте свої бронювання на `/my-bookings`
7. Скасуйте бронювання (якщо потрібно)

### Для менеджера (manager):

1. Увійдіть як менеджер
2. Перейдіть в адміністративну панель `/admin`
3. Вкладка "Manage Rooms":
   - Створіть новий номер
   - Відредагуйте існуючий номер
   - Видаліть номер
   - Змініть доступність номера
4. Вкладка "View Bookings":
   - Перегляньте всі бронювання
   - Перевірте статуси

## Структура проекту

```
курсова/
├── backend/                 # Backend API
│   ├── app/
│   │   ├── models/         # Моделі БД
│   │   ├── controllers/    # Бізнес-логіка
│   │   ├── views/          # API endpoints
│   │   ├── schemas/        # Pydantic схеми
│   │   ├── repositories/   # Репозиторії
│   │   ├── dependencies/   # DI
│   │   ├── core/           # Конфігурація
│   │   └── database/       # БД підключення
│   ├── alembic/            # Міграції
│   └── pyproject.toml      # Залежності
├── frontend/               # Frontend React app
│   ├── src/
│   │   ├── components/     # React компоненти
│   │   ├── pages/          # Сторінки
│   │   ├── services/       # API сервіси
│   │   ├── contexts/       # React contexts
│   │   └── styles/         # CSS
│   └── package.json        # Залежності
└── README.md               # Документація
```

## Корисні команди

### Backend

```bash
# Активувати віртуальне середовище Poetry
poetry shell

# Запустити сервер
poetry run uvicorn app.main:app --reload

# Створити міграцію
poetry run alembic revision --autogenerate -m "description"

# Застосувати міграції
poetry run alembic upgrade head

# Відкотити міграцію
poetry run alembic downgrade -1

# Запустити тести
poetry run pytest
```

### Frontend

```bash
# Встановити залежності
npm install

# Запустити dev сервер
npm start

# Збудувати для продакшн
npm run build

# Запустити тести
npm test
```

## Troubleshooting

### Backend не запускається

1. Перевірте змінні в `.env` (особливо DATABASE_URL)
2. Перевірте, що міграції застосовані: `poetry run alembic current`
3. Перевірте права на запис файлів в папці backend

### Frontend не може з'єднатися з Backend

1. Перевірте, що backend запущений на `http://localhost:8000`
2. Перевірте змінну `REACT_APP_API_URL` в `.env`
3. Перевірте CORS налаштування в backend

### Помилки міграцій

```bash
# Скинути всі міграції (УВАГА: видалить дані!)
poetry run alembic downgrade base

# Застосувати знову
poetry run alembic upgrade head
```

### Забули пароль менеджера

Оновіть пароль в базі даних:

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("new_password")
print(hashed)
```

Потім виконайте SQL:

```sql
UPDATE users SET hashed_password = 'вставте_хеш' WHERE username = 'manager';
```

## Безпека

### Для розробки

- Використовуйте прості паролі
- SECRET_KEY може бути простим

### Для продакшн

- Згенеруйте надійний SECRET_KEY: `openssl rand -hex 32`
- Використовуйте надійні паролі для БД
- Увімкніть HTTPS
- Налаштуйте CORS правильно
- Змініть `DEBUG=False` в налаштуваннях

## Підтримка

При виникненні проблем:

1. Перевірте логи backend та frontend
2. Перевірте API документацію: http://localhost:8000/docs
3. Перевірте консоль браузера на помилки

## Ліцензія

Навчальний проєкт для курсової роботи.
