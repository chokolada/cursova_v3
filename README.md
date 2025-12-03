# Система Управління Готелем

Повнофункціональна система управління готелем з веб-інтерфейсом для клієнтів та адміністративною панеллю для менеджерів.

## Технологічний Стек

### Backend
- **FastAPI** - сучасний веб-фреймворк для створення API
- **SQLite** - легка реляційна база даних (файлова, не потребує окремого сервера)
- **SQLAlchemy** - ORM для роботи з базою даних
- **Alembic** - міграції бази даних
- **Poetry** - управління залежностями
- **Pydantic** - валідація даних
- **Python-Jose** - JWT токени
- **Passlib + Bcrypt** - хешування паролів

### Frontend
- **React** - JavaScript бібліотека для побудови UI
- **React Router** - маршрутизація
- **Axios** - HTTP клієнт
- **Material-UI / Tailwind CSS** - UI компоненти

## Функціонал

### Для Клієнтів (Користувачів Готелю)
- Перегляд доступних номерів
- Бронювання номерів
- Перегляд історії бронювань
- Реєстрація та авторизація

### Для Менеджерів (Адміністративна Панель)
- Управління номерами (створення, редагування, видалення)
- Управління бронюваннями
- Перегляд статистики
- Управління користувачами

## Архітектура

### Backend (MVC Pattern)
```
backend/
├── app/
│   ├── models/          # Моделі бази даних (SQLAlchemy)
│   ├── controllers/     # Контролери (бізнес-логіка)
│   ├── views/           # Views (API endpoints/routes)
│   ├── schemas/         # Pydantic схеми (валідація)
│   ├── services/        # Сервіси (додаткова логіка)
│   ├── repositories/    # Репозиторії (доступ до БД)
│   ├── dependencies/    # Dependency Injection
│   ├── core/            # Конфігурація, безпека, JWT
│   └── database/        # Підключення до БД
├── alembic/             # Міграції
├── tests/               # Тести
└── pyproject.toml       # Poetry конфігурація
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/      # React компоненти
│   ├── pages/           # Сторінки (Hotel, Admin)
│   ├── services/        # API calls
│   ├── contexts/        # React Context (auth, state)
│   ├── hooks/           # Custom hooks
│   └── utils/           # Утиліти
├── public/
└── package.json
```

## Безпека

### Авторизація та Аутентифікація
- **JWT (JSON Web Tokens)** для авторизації
- **Bcrypt** для хешування паролів
- **Role-Based Access Control (RBAC)** - розділення прав доступу:
  - `user` - звичайний користувач (клієнт готелю)
  - `manager` - менеджер готелю (адміністратор)
  - `admin` - системний адміністратор

### Dependency Injection
- Використання FastAPI Depends для DI
- Репозиторії впроваджуються через DI
- Сервіси впроваджуються через DI

## База Даних

### Основні Таблиці
- **users** - користувачі системи
- **rooms** - номери готелю
- **bookings** - бронювання
- **room_types** - типи номерів

## Налаштування та Запуск

### Backend

1. Встановіть Poetry:
```bash
pip install poetry
```

2. Встановіть залежності:
```bash
cd backend
poetry install
```

3. Створіть файл `.env`:
```env
DATABASE_URL=sqlite+aiosqlite:///./hotel.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Запустіть міграції (база даних створиться автоматично):
```bash
poetry run alembic upgrade head
```

5. Запустіть сервер:
```bash
poetry run uvicorn app.main:app --reload
```

### Frontend

1. Встановіть залежності:
```bash
cd frontend
npm install
```

2. Створіть файл `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

3. Запустіть сервер розробки:
```bash
npm start
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - реєстрація
- `POST /api/auth/login` - вхід
- `POST /api/auth/refresh` - оновлення токена

### Rooms
- `GET /api/rooms` - список номерів
- `GET /api/rooms/{id}` - деталі номера
- `POST /api/rooms` - створити номер (manager)
- `PUT /api/rooms/{id}` - оновити номер (manager)
- `DELETE /api/rooms/{id}` - видалити номер (manager)

### Bookings
- `GET /api/bookings` - мої бронювання
- `POST /api/bookings` - створити бронювання
- `GET /api/bookings/all` - всі бронювання (manager)
- `PUT /api/bookings/{id}` - оновити бронювання
- `DELETE /api/bookings/{id}` - скасувати бронювання

### Users (Manager only)
- `GET /api/users` - список користувачів
- `GET /api/users/{id}` - деталі користувача
- `PUT /api/users/{id}` - оновити користувача
- `DELETE /api/users/{id}` - видалити користувача

## Тестування

```bash
cd backend
poetry run pytest
```

## Автори

Курсова робота з дисципліни "Додатки прикладного захисту систем та протоколів"

## Ліцензія

Навчальний проєкт
