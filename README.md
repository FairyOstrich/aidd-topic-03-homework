# Investing Demo

Веб-приложение на Django для просмотра каталога акций, котировок и графиков.

## Установка и запуск

Требуется Python 3.10 или новее. Создайте и активируйте виртуальное окружение,
затем установите зависимости и примените миграции:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Для локального запуска по умолчанию используется SQLite. PostgreSQL можно
запустить через Docker Compose:

```powershell
docker compose up -d db redis
```

Чтобы выбрать PostgreSQL, задайте переменные окружения:
`DB_ENGINE=django.db.backends.postgresql`, `DB_NAME=investing`,
`DB_USER=postgres`, `DB_PASSWORD=postgres`, `DB_HOST=localhost`,
`DB_PORT=5432`.

Для локальной разработки используется тестовый `DJANGO_SECRET_KEY` по
умолчанию. Перед развертыванием задайте свой `DJANGO_SECRET_KEY`, установите
`DJANGO_DEBUG=false` и укажите список хостов через `DJANGO_ALLOWED_HOSTS`.

## Котировки Tinkoff и Celery

Рыночные данные загружаются через официальный Tinkoff Invest SDK. SDK больше
не устанавливается из PyPI; для его добавления установите зафиксированную
версию из официального репозитория после основных зависимостей:

```powershell
python -m pip install --no-deps -r requirements-market.txt
```

Укажите API-токен в переменной окружения `TINKOFF_TOKEN`. Для первоначальной
загрузки инструментов:

```powershell
python manage.py add_shares
```

Для периодического обновления цены нужны запущенные Redis и два процесса:

```powershell
celery -A config beat
celery -A config worker -l info
```

Задача обновления настроена на интервал 5 минут. Без SDK или токена приложение
запускается, но функции получения рыночных данных недоступны.

## История цен

При каждом успешном обновлении задачи Celery снимок цены записывается в
`PriceHistory` с рыночной временной меткой. На странице акции можно выбрать
период (день, 7/30/90/180 дней или всё время), увидеть график сохранённых
котировок и изменение цены в абсолютном и процентном выражении. История
начинает накапливаться после запуска Celery Worker и первого успешного запроса
к Tinkoff API.

Чтобы посмотреть график без подключения к Tinkoff API, создайте
демонстрационную акцию с явно помеченными синтетическими данными:

```powershell
python manage.py add_demo_history
```

На главной странице у каждой акции есть кнопка «История цен». Для реальных
акций при первом открытии истории загружаются дневные свечи Tinkoff (при
установленном SDK и настроенном `TINKOFF_TOKEN`); последующие снимки сохраняет
Celery Worker.

## API

REST API акций доступен по адресу `/api/v1/shares/`. Поддерживаются CRUD,
фильтрация по названию и тикеру, поиск и сортировка.

## Проверки

```powershell
python manage.py check
python manage.py test dashboard user
```
