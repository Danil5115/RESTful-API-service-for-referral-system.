# RESTful-API-service-for-referral-system.
# Реферальная Система
### Описание
Проект представляет собой RESTful API сервис для реферальной системы. Пользователи могут регистрироваться, аутентифицироваться через JWT Oauth 2.0, создавать и удалять свои реферальные коды, получать реферальный код по email адресу реферера, регистрироваться по реферальному коду, а также получать информацию о своих рефералах.

### Технологии
* Django & Django REST Framework для backend части.
* JWT для аутентификации.
* SQLite для базы данных.
* drf-yasg для генерации Swagger UI документации.

### Установка и Запуск
1. Клонируйте репозиторий:
``` git clone https://github.com/Danil5115/RESTful-API-service-for-referral-system..git
```
3. Создание виртуального окружения:
``` python -m venv venv 
.\venv\Scripts\activate
```
3. Установка зависимостей
``` pip install -r requirements.txt
```
5. Перейдите в папку проекта referral_project
6. Миграции. Примените миграции для создания таблиц в базе данных:
``` python manage.py migrate
```
8. Запуск сервера:
``` python manage.py runserver
```
