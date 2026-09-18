# JSON-RPC console

Тестовое задание (qualixDev, backend Python/Django). Django-клиент к
JSON-RPC 2.0 сервису (`https://slb.medv.ru/api/v2/`), авторизация — двусторонний
TLS (клиентский сертификат + ключ).

## Перед первым запуском

Создайте файл `local_secrets.py` в корне проекта, рядом с `manage.py`.

```python
import os

os.environ["DJANGO_SECRET_KEY"] = (
    "значение, которое сгенерировал django-admin startproject"
)

os.environ["CLIENT_CERT_PEM"] = """-----BEGIN CERTIFICATE-----
...содержимое client2026test.crt целиком...
-----END CERTIFICATE-----
"""

os.environ["CLIENT_KEY_PEM"] = """-----BEGIN PRIVATE KEY-----
...содержимое client2026test.key целиком...
-----END PRIVATE KEY-----
"""
```

## Установка

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Запуск

```bash
.venv/bin/python manage.py runserver
```

## Тесты

```bash
.venv/bin/python manage.py test
```