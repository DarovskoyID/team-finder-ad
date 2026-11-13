# TeamFinder

Поиск команды для совместных проектов. Django 5.2, PostgreSQL 16.
Вариант №3: навыки проектов и фильтрация по ним.

## Быстрый запуск

Нужны Python 3.11+ и запущенный Docker Desktop.
В терминале:

```bash
git clone https://github.com/DarovskoyID/team-finder-ad.git
cd team-finder-ad
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env_example .env
```

В Windows окружение активируется командой `.venv\Scripts\activate`.
Если `.env` уже настроен, не заменяйте его.

В `.env` замените `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD`.
Остальные значения из примера подходят для локального запуска.
Получить случайный ключ:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Затем:

```bash
docker compose up -d
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Сайт: [localhost:8000](http://localhost:8000).
Админка: [localhost:8000/admin/](http://localhost:8000/admin/).

Если PostgreSQL уже работает, укажите его параметры в `.env`
и пропустите `docker compose up -d`.
Данные Docker сохраняются в томе `postgres_data`.

## Тестовые аккаунты

`seed_demo` создаёт 15 пользователей, 15 проектов и 12 навыков.
Повторный запуск не создаёт дубликаты.

- Администратор: `admin@example.com`.
- Пользователи: `demo1@example.com` … `demo14@example.com`.
- Пароль для всех: `TeamFinder-demo-42!`.

Полностью очистить данные TeamFinder и заполнить заново:

```bash
python manage.py seed_demo --reset
```

**`--reset` удаляет текущих пользователей, проекты и навыки.**

## Проверка

```bash
pip install -r requirements-dev.txt
python manage.py test --noinput
python -m pycodestyle projects users team_finder manage.py
python -m black --check projects users team_finder manage.py
```

Тесты создают отдельную временную PostgreSQL-базу: пользователь БД
должен иметь право её создания. Лимит строки Python — 70 символов.
