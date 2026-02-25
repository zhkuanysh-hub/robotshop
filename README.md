# RobotShop

## Описание RobotShop
RobotShop — Django-проект интернет-магазина роботов с каталогом, корзиной, заказами, блогом и информационными страницами.

## Стек
- Python 3
- Django
- SQLite (по умолчанию)
- python-dotenv
- HTML/CSS (шаблоны на базе HTML5 UP Escape Velocity)

## Установка
```bash
git clone <repo-url>
cd robotshop
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
# source venv/bin/activate
pip install -r requirements.txt
```

## Миграции и создание суперпользователя
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Запуск
```bash
python manage.py runserver
```

## Статика (production-ready)
```bash
python manage.py collectstatic --noinput
```

## Тесты
```bash
python manage.py test
```

## Переменные окружения (.env и .env.example)
Создайте `.env` в корне проекта (рядом с `manage.py`) на основе `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

Проверка локально (production-режим):
```bash
# в .env установите DEBUG=False
python manage.py collectstatic --noinput
python manage.py runserver --insecure
```

## Структура приложений (apps)
- `apps/core` — главная, информационные страницы, общие обработчики
- `apps/blog` — блог
- `accounts` — аккаунты/профиль
- `catalog` — каталог роботов
- `cart` — корзина
- `orders` — заказы
- `reviews` — отзывы
- `wishlist` — избранное
- `payments` — оплаты
- `shipping` — доставка
- `inventory` — склад
- `api` — API endpoints

## Полезные URL
- `/` — главная
- `/catalog/` — каталог
- `/cart/` — корзина
- `/admin/` — админ-панель

## API
Базовый URL: `/api/`

Эндпоинты:
- `GET /api/robots/` — список роботов (фильтры: `q`, `brand`, `category`, `min_price`, `max_price`, `ordering`, `page`, `page_size`)
- `GET /api/robots/<id>/` — детали робота
- `GET /api/brands/` — список брендов
- `GET /api/categories/` — список категорий
- `POST /api/robots/` — создать робота (только staff)
- `PUT /api/robots/<id>/` — обновить робота (только staff)
- `DELETE /api/robots/<id>/` — удалить робота (только staff)

Примеры:
```bash
curl "http://127.0.0.1:8000/api/robots/?q=helper&ordering=-price&page=1&page_size=10"
curl "http://127.0.0.1:8000/api/robots/1/"
curl -X POST "http://127.0.0.1:8000/api/robots/" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Bot\",\"price\":\"1200.00\",\"brand_id\":1,\"category_id\":1}"
```

Формат успешного ответа:
```json
{"ok": true, "data": {}}
```

Формат ошибки:
```json
{"ok": false, "error": {"code": "bad_request", "message": "...", "details": {}}}
```

## TODO: домен/деплой
TODO

## Deploy on Render
Build command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start command:
```bash
python manage.py migrate && gunicorn config.wsgi:application
```

Required environment variables:
- `SECRET_KEY`
- `DEBUG` (`False` on production)
- `ALLOWED_HOSTS` (comma-separated, e.g. `example.com,www.example.com`)
- `DATABASE_URL` (PostgreSQL URL from Render)
- `CSRF_TRUSTED_ORIGINS` (comma-separated https origins)

## Примечание по InvalidOperation
Если появляется ошибка `decimal.InvalidOperation` на заказах, это обычно означает поврежденные или переполненные decimal-значения в `orders_order.total_amount` / `orders_orderitem.unit_price`.

Исправление:
```bash
python manage.py fix_order_decimals
```
