### QRkot - благотворительный проект для сбора пожертвований для кошек, основанный на технологии FAST API.

##### Технологии:
+ fastapi
+ uvicorn
+ sqlalchemy
+ pydantic
+ alembic

##### Чтобы запустить проект, нужно:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Запустить приложение через uvicorn

```
uvicorn app.main:app --reload
```

Не забываем про миграции

```
alembic revision --autogenerate -m "First migration"
alembic upgrade head

```
