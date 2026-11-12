# TeamFinder

Платформа поиска команды для совместных проектов на Django 5.2.
Реализован вариант №3: необходимые навыки проектов и фильтрация.

## Запуск

Требуются Python 3.11+, Docker и Docker Compose.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env_example .env
```

В `.env` задайте секретный ключ Django и параметры PostgreSQL.
Ключ можно получить командой:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Если база уже работает, укажите её параметры в `.env` и пропустите
запуск Docker. Не создавайте второй контейнер на том же порту.

```bash
docker compose up -d
python manage.py migrate
python manage.py runserver
```

Открыть приложение: [localhost:8000](http://localhost:8000).
PostgreSQL хранит данные в именованном томе `postgres_data`.

## Демонстрационные данные

```bash
python manage.py seed_demo
```

Команда создаёт 15 пользователей, по проекту для каждого, 12 навыков
и участников проектов. Есть открытые и закрытые проекты.
Повторный запуск не создаёт дубликаты демонстрационных записей.

Для удаления текущих данных TeamFinder и повторного заполнения:

```bash
python manage.py seed_demo --reset
```

`--reset` удаляет всех пользователей, проекты, навыки, сессии и журнал
администратора в подключённой базе. Используйте только для тестовой базы.

Демонстрационные аккаунты:

- Администратор: `admin@example.com`.
- Пользователи: `demo1@example.com` … `demo14@example.com`.
- Общий пароль: `TeamFinder-demo-42!`.

Пароль для новых демонстрационных аккаунтов можно задать самостоятельно:

```bash
python manage.py seed_demo --password 'Your-local-password'
```

Админка: [localhost:8000/admin/](http://localhost:8000/admin/).

## Проверка

```bash
python -m pip install -r requirements-dev.txt
python manage.py test --noinput
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pycodestyle projectManager userManager team_finder manage.py
python -m black --check projectManager userManager team_finder manage.py
```

Тесты используют отдельную временную базу PostgreSQL.
Пользователю БД нужны права создания тестовой базы.
Данные рабочей базы при тестировании не изменяются.
Максимальная длина строки Python — 70 символов.

## Решения по требованиям

- Используются маршруты `/projects/`, как в предоставленных шаблонах.
- После регистрации пользователь переходит на страницу входа,
  согласно функциональному описанию задания.
- Избранное и навыки пользователей относятся к вариантам №1 и №2.
- Профиль поддерживает загрузку аватара и стандартную картинку.
  Для новых пользователей создаётся PNG с первой буквой имени.
- Телефон необязателен при регистрации и редактировании. Заполненный
  номер проверяется, приводится к `+7XXXXXXXXXX` и должен быть уникален.
- Ссылки на GitHub проверяются в формах и при валидации моделей.
- Проверка сложности паролей работает также в режиме отладки.
- `.env`, файлы пользователей и личные настройки PyCharm исключены из Git.
