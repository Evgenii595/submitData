"""
Модели данных для API перевалов ФСТР
Используется Pydantic для валидации данных
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class UserData(BaseModel):
    """Модель данных пользователя"""
    email: str = Field(..., description="Email пользователя")
    phone: str = Field(..., description="Телефон пользователя")
    fam: str = Field(..., description="Фамилия")
    name: str = Field(..., description="Имя")
    otc: Optional[str] = Field(None, description="Отчество")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Некорректный email')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        # Убираем все нецифровые символы для проверки
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 10:
            raise ValueError('Некорректный номер телефона')
        return v


class Coordinates(BaseModel):
    """Модель координат перевала"""
    latitude: str = Field(..., description="Широта")
    longitude: str = Field(..., description="Долгота")
    height: str = Field(..., description="Высота")
    
    @validator('latitude', 'longitude', 'height')
    def validate_coordinates(cls, v):
        try:
            float(v)
        except ValueError:
            raise ValueError('Координаты должны быть числовыми')
        return v


class Level(BaseModel):
    """Модель категорий трудности по сезонам"""
    winter: Optional[str] = Field(None, description="Категория трудности зимой")
    summer: Optional[str] = Field(None, description="Категория трудности летом")
    autumn: Optional[str] = Field(None, description="Категория трудности осенью")
    spring: Optional[str] = Field(None, description="Категория трудности весной")


class ImageData(BaseModel):
    """Модель данных изображения"""
    data: str = Field(..., description="Данные изображения в base64")
    title: str = Field(..., description="Название изображения")


class PerevalSubmitData(BaseModel):
    """Основная модель данных для отправки перевала"""
    beauty_title: Optional[str] = Field(None, description="Красивое название")
    title: str = Field(..., description="Название перевала")
    other_titles: Optional[str] = Field(None, description="Другие названия")
    connect: Optional[str] = Field(None, description="Что соединяет")
    add_time: Optional[str] = Field(None, description="Время добавления")
    user: UserData = Field(..., description="Данные пользователя")
    coords: Coordinates = Field(..., description="Координаты")
    level: Level = Field(..., description="Категории трудности")
    images: List[ImageData] = Field(default=[], description="Изображения")
    
    @validator('add_time')
    def validate_add_time(cls, v):
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError('Некорректный формат времени. Используйте: YYYY-MM-DD HH:MM:SS')
        return v


class PerevalResponse(BaseModel):
    """Модель ответа API"""
    status: int = Field(..., description="HTTP статус код")
    message: Optional[str] = Field(None, description="Сообщение")
    id: Optional[int] = Field(None, description="ID созданной записи")


class PerevalStatus(str):
    """Enum для статусов модерации"""
    NEW = "new"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
