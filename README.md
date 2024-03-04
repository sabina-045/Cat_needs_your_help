### Cat_needs_your_help - благотворительный проект для сбора пожертвований для кошек, основанный на технологии FAST API.
>В проекте может быть открыто несколько целевых проектов. У каждого проекта есть название, описание и сумма, которую планируется собрать. После того, как нужная сумма собрана — проект закрывается.
Пожертвования в проекты поступают по принципу First In, First Out: все пожертвования идут в проект, открытый раньше других; когда этот проект набирает необходимую сумму и закрывается — пожертвования начинают поступать в следующий проект. Также в проекте формируется отчет в виде google-таблицы с закрытыми проектами, отсортированными по скорости сбора средств.

##### Технологии:
+ fastapi
+ uvicorn
+ sqlalchemy
+ pydantic
+ alembic

##### Чтобы запустить проект, нужно:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:sabina-045/Cat_needs_your_help.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS:

    ```
    source venv/bin/activate
    ```

* Если у вас Windows:

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить приложение через uvicorn:

```
uvicorn app.main:app --reload
```

Не забываем про миграции:


```
alembic revision --autogenerate -m "First migration"
alembic upgrade head

```
Основные эндпойнты:

```

/charity_project/ - получить список всех проектов, создать проект (только суперюзером)
/charity_project/{project_id} - редактировать или удалить проекта (только суперюзером)
/donation/ - сделать пожертвование, получить список всех пожертвований (только суперюзером)
/donation/my - вернуть список пожертвований пользователя, выполняющего запрос

```
_По умолчанию доступ только у авторизованных пользователей._
_Аутентификация через JWT token._
</br>
</br>
> Команда создателей:
Яндекс Практикум, Сабина Гаджиева.
