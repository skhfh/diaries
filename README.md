# Yatube: Социальная сеть для публикации дневников

**Yatube** — это социальная сеть, где пользователи могут публиковать свои записи, 
прикреплять к ним изображения, читать и комментировать чужие посты, а также 
подписываться на авторов.

## Возможности

- Публикация личных записей и добавление изображений к постам
- Комментирование записей других пользователей
- Подписка на авторов
- Создание тематических сообществ (доступно только администраторам)
- Публикация записей в тематических сообществах
- Пагинация постов и кеширование главной страницы
- Восстановление паролей через почту
- Кастомные шаблоны страниц ошибок (например, 404 и 500), которые улучшают UX при возникновении ошибок

## Технологии

- **Python 3.9**
- **Django 2.2**
- **SQLite3**
- **Unittest**
- **HTML**
- **CSS**

## Запуск проекта в режиме разработки

1. Клонируйте репозиторий:
    ```bash
    git clone git@github.com:skhfh/diaries.git
    ```

2. Перейдите в директорию проекта и создайте виртуальное окружение:
    ```bash
    cd diaries
    python -m venv venv
    ```

3. Активируйте виртуальное окружение:
    ```bash
    source venv/Scripts/activate  # Windows
    source venv/bin/activate       # macOS/Linux
    ```

4. Установите зависимости из файла `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

5. Примените миграции для создания базы данных:
    ```bash
    python manage.py migrate
    ```

6. Запустите проект:
    ```bash
    python manage.py runserver
    ```

7. Откройте браузер и перейдите по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Примеры использования

После регистрации пользователи могут:
- Создать свою страницу, на которой отображаются их записи.
- Просматривать записи других пользователей и оставлять комментарии.
- Подписываться на авторов и получать обновления их записей в своей ленте.
- Публиковать записи в тематических сообществах, созданных администратором.

## Структура проекта

- `yatube/` — директория с настройками и конфигурацией проекта.
- `posts/` — приложение для управления постами, комментариями и сообществами.
- `users/` — приложение для управления пользователями, их регистрацией и аутентификацией.
- `templates/` — HTML-шаблоны для страниц сайта, включая кастомные страницы ошибок (например, 404 и 500).
- `static/` — статические файлы, включая CSS.

## Тестирование

Тесты написаны с использованием `unittest`. Чтобы запустить тесты, выполните команду:
```bash
python manage.py test
```
---
## Автор проекта
[skhfh](https://github.com/skhfh)
