"""
REST API для ФСТР - система управления перевалами
Основной файл приложения FastAPI
"""

import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.db_manager import DatabaseManager
from models.pereval_models import PerevalSubmitData, PerevalResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для менеджера БД
db_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global db_manager
    
    # Инициализация при запуске
    db_manager = DatabaseManager()
    if not db_manager.connect():
        logger.error("Не удалось подключиться к базе данных")
        raise Exception("Ошибка подключения к БД")
    
    logger.info("Приложение запущено")
    yield
    
    # Очистка при завершении
    if db_manager:
        db_manager.disconnect()
    logger.info("Приложение остановлено")


# Создание приложения FastAPI
app = FastAPI(
    title="ФСТР API - Система управления перевалами",
    description="REST API для мобильного приложения ФСТР по управлению базой горных перевалов",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS для работы с мобильными приложениями
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно ограничить домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой endpoint для проверки работы API"""
    return {
        "message": "ФСТР API - Система управления перевалами",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка состояния API и подключения к БД"""
    global db_manager
    
    if not db_manager or not db_manager.connection:
        return {
            "status": "error",
            "message": "Нет подключения к базе данных"
        }
    
    try:
        # Проверяем подключение к БД
        with db_manager.connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return {
            "status": "ok",
            "message": "API и база данных работают корректно"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ошибка подключения к БД: {str(e)}"
        }


@app.post("/submitData", response_model=PerevalResponse)
async def submit_data(pereval_data: PerevalSubmitData):
    """
    Метод для отправки данных о перевале
    
    Принимает JSON с информацией о перевале и сохраняет в базу данных.
    Возвращает статус операции и ID созданной записи.
    """
    global db_manager
    
    if not db_manager:
        logger.error("Менеджер БД не инициализирован")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка инициализации базы данных"
        )
    
    try:
        # Валидация обязательных полей
        if not pereval_data.title:
            return PerevalResponse(
                status=400,
                message="Отсутствует обязательное поле: title",
                id=None
            )
        
        if not pereval_data.coords:
            return PerevalResponse(
                status=400,
                message="Отсутствуют обязательные поля: coords",
                id=None
            )
        
        if not pereval_data.user:
            return PerevalResponse(
                status=400,
                message="Отсутствуют обязательные поля: user",
                id=None
            )
        
        # Преобразуем Pydantic модель в словарь
        pereval_dict = pereval_data.dict()
        
        # Добавляем перевал в базу данных
        pereval_id = db_manager.add_pereval(pereval_dict)
        
        if pereval_id is None:
            logger.error("Не удалось добавить перевал в БД")
            return PerevalResponse(
                status=500,
                message="Ошибка при сохранении данных в базу данных",
                id=None
            )
        
        logger.info(f"Успешно добавлен перевал с ID: {pereval_id}")
        return PerevalResponse(
            status=200,
            message="Отправлено успешно",
            id=pereval_id
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}")
        return PerevalResponse(
            status=500,
            message=f"Внутренняя ошибка сервера: {str(e)}",
            id=None
        )


@app.get("/pereval/{pereval_id}")
async def get_pereval(pereval_id: int):
    """
    Получение данных о перевале по ID
    
    Args:
        pereval_id: ID перевала
        
    Returns:
        Данные о перевале или ошибку
    """
    global db_manager
    
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка инициализации базы данных"
        )
    
    pereval_data = db_manager.get_pereval_by_id(pereval_id)
    
    if not pereval_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Перевал с ID {pereval_id} не найден"
        )
    
    return pereval_data


@app.get("/submitData/{pereval_id}")
async def get_pereval_by_id(pereval_id: int):
    """
    Получение записи о перевале по ID
    
    Args:
        pereval_id: ID перевала
        
    Returns:
        Данные о перевале с полной информацией включая статус модерации
    """
    global db_manager
    
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка инициализации базы данных"
        )
    
    pereval_data = db_manager.get_pereval_by_id(pereval_id)
    
    if not pereval_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Перевал с ID {pereval_id} не найден"
        )
    
    return pereval_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
