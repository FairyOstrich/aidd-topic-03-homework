# ANALYSIS.md — Анализ приложения Investing Demo

## Назначение приложения
Десктопное приложение для отслеживания акций: хранит список инструментов, отображает графики цен за 180 дней и периодически обновляет текущую цену через Tinkoff Invest API. Предоставляет HTML-интерфейс (CRUD), REST API и личный портфель позиций. Оформлено в тёмной теме, запускается в собственном окне (не в браузере).

## Технологический стек
- Python 3, Django 4.1.7
- БД: SQLite (`db.sqlite3`) для локального запуска (PostgreSQL в `docker-compose.yml`)
- Очереди: Celery + Redis (broker `redis://127.0.0.1:6379/0`)
- REST: Django REST Framework + django-filter
- Фронтенд: Django templates, Bootstrap 3 (crispy_forms), Plotly, тёмная тема
- Десктопная обёртка: `pywebview` (WebView2 на Windows)
- Внешний API: Tinkoff Invest (`tinkoff` — заглушка, реальный токен не настроен)

## Структура проекта
- `config/` — настройки Django, URL-корень, Celery app, WSGI/ASGI
- `dashboard/` — основное приложение: модели `Share` и `Position`, views, формы, admin, API v1, сервисы, celery-задачи, шаблоны
- `user/` — аутентификация/регистрация (стандартный User), шаблоны входа/регистрации с тёмной темой
- `tinkoff/` — заглушка SDK Tinkoff (реальный пакет недоступен)
- `desktop_app.py` — лаунчер десктопного приложения (запускает Django + pywebview окно)
- `Запустить Инвестиции.bat` — двойным кликом запускает приложение
- `manage.py` — точка входа Django

## Основные компоненты и их назначение
- `config.settings` — конфигурация, БД (SQLite), Celery, логирование, Tinkoff token (пустой), SECRET_KEY (временный dev)
- `dashboard.models.Share` — сущность акции
- `dashboard.models.Position` — позиция пользователя (user FK, share FK, quantity, purchase_price, purchased_at, unique_together user+share)
- `dashboard.views` — ListView/DetailView/Create/Update/Delete для акций; `PositionListView/CreateView/UpdateView/DeleteView` для портфеля; `IsUserAuthenticatedMixin` защищает create/update/delete
- `dashboard.api.v1.ShareViewSet` — REST CRUD с фильтрацией/поиском/сортировкой
- `dashboard.services.market_data.get_last_data` — получение последней цены по figi
- `dashboard.services.graph.get_graph` — график свечей за 180 дней (Plotly)
- `dashboard.tasks.update_last_price` — Celery-задача обновления цен и тренда
- `user.views` — AuthView, RegistrationView, LogoutView
- `desktop_app.start_django_process` — запуск Django как subprocess
- `desktop_app.wait_for_server` — ожидание доступности сервера

## Модель данных
- `Share`:
  - `figi` (unique), `isin`, `name`, `ticker` (unique, max 10), `currency`, `uid` (unique)
  - `last_price` (Float, nullable), `is_trend_high` (bool, nullable), `updated_at` (auto_now)
- `Position`:
  - `user` (FK auth.User), `share` (FK Share), `quantity` (PositiveInteger), `purchase_price` (Decimal 12,2), `purchased_at` (auto_now_add)
  - `unique_together = ("user", "share")`
- Пользователи — стандартная модель Django `auth.User`.

Связей между моделями нет (кроме FK Position→User, Position→Share).

## Обработка запросов и работу с БД
- Маршруты: `/` (список акций), `/<pk>` (деталь с графиком), `/create|update|delete/<pk>` (акции); `/portfolio/`, `/portfolio/create`, `/portfolio/update/<pk>`, `/portfolio/delete/<pk>` (портфель); `/userlogin/`, `/userregistration/`, `/userlogout/` (аутентификация); `/admin/`; `/api/v1/shares/` (DRF).
- Запросы обрабатываются Django views + DRF ViewSet (ORM → SQLite/PostgreSQL).
- Фоновые обновления: Celery beat запускает `update_last_price`; задача запрашивает Tinkoff API и обновляет `last_price`/`is_trend_high`.
- Десктопное окно: `desktop_app.py` запускает Django subprocess + pywebview окно `http://127.0.0.1:8000/`.

## Замечания
- `SECRET_KEY` — временный dev-ключ, не для продакшена.
- `DEBUG=True`, `ALLOWED_HOSTS=[]` — конфиг не для продакшена.
- `TINKOFF_TOKEN` пустой — сервисы Tinkoff и графики не работают без реального токена.
- `tinkoff/` — заглушка, реальный пакет `tinkoff-investments` не установлен.
- Celery beat/worker нужно запускать отдельно.
- БД по умолчанию SQLite; для PostgreSQL раскомментировать блок в `config/settings.py`.
