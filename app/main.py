from fastapi import FastAPI

from app.api.routers import main_router
# Импортируем настройки проекта из config.py.
from app.core.config import settings

# Устанавливаем заголовок приложения при помощи аргумента title,
# в качестве значения указываем атрибут app_title объекта settings.
app = FastAPI(title=settings.app_title, docs_url='/swagger')

app.include_router(main_router)
