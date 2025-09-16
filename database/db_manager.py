"""
Класс для работы с базой данных PostgreSQL
Обрабатывает подключение и операции с данными о перевалах
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Класс для управления подключением и операциями с базой данных"""
    
    def __init__(self):
        """Инициализация подключения к БД через переменные окружения"""
        self.host = os.getenv('FSTR_DB_HOST', 'localhost')
        self.port = os.getenv('FSTR_DB_PORT', '5432')
        self.login = os.getenv('FSTR_DB_LOGIN', 'postgres')
        self.password = os.getenv('FSTR_DB_PASS', 'password')
        self.database = os.getenv('FSTR_DB_NAME', 'pereval')
        self.connection = None
    
    def connect(self) -> bool:
        """
        Установка подключения к базе данных
        
        Returns:
            bool: True если подключение успешно, False в противном случае
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.login,
                password=self.password,
                database=self.database,
                cursor_factory=RealDictCursor
            )
            logger.info("Успешное подключение к базе данных")
            return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def disconnect(self):
        """Закрытие подключения к базе данных"""
        if self.connection:
            self.connection.close()
            logger.info("Подключение к базе данных закрыто")
    
    def get_or_create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """
        Получение существующего пользователя или создание нового
        
        Args:
            user_data: Словарь с данными пользователя
            
        Returns:
            int: ID пользователя или None в случае ошибки
        """
        if not self.connection:
            logger.error("Нет подключения к базе данных")
            return None
        
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, существует ли пользователь с таким email
                cursor.execute(
                    "SELECT id FROM pereval_users WHERE email = %s",
                    (user_data['email'],)
                )
                existing_user = cursor.fetchone()
                
                if existing_user:
                    logger.info(f"Найден существующий пользователь с ID: {existing_user['id']}")
                    return existing_user['id']
                
                # Создаем нового пользователя
                cursor.execute("""
                    INSERT INTO pereval_users (email, phone, fam, name, otc)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_data['email'],
                    user_data['phone'],
                    user_data['fam'],
                    user_data['name'],
                    user_data.get('otc', '')
                ))
                
                user_id = cursor.fetchone()['id']
                self.connection.commit()
                logger.info(f"Создан новый пользователь с ID: {user_id}")
                return user_id
                
        except psycopg2.Error as e:
            logger.error(f"Ошибка при работе с пользователем: {e}")
            self.connection.rollback()
            return None
    
    def add_pereval(self, pereval_data: Dict[str, Any]) -> Optional[int]:
        """
        Добавление нового перевала в базу данных
        
        Args:
            pereval_data: Словарь с данными о перевале
            
        Returns:
            int: ID добавленного перевала или None в случае ошибки
        """
        if not self.connection:
            logger.error("Нет подключения к базе данных")
            return None
        
        try:
            with self.connection.cursor() as cursor:
                # Получаем или создаем пользователя
                user_id = self.get_or_create_user(pereval_data['user'])
                if not user_id:
                    return None
                
                # Подготавливаем данные для вставки
                add_time = None
                if pereval_data.get('add_time'):
                    try:
                        add_time = datetime.strptime(pereval_data['add_time'], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        add_time = datetime.now()
                else:
                    add_time = datetime.now()
                
                # Вставляем данные о перевале
                cursor.execute("""
                    INSERT INTO pereval_added (
                        beauty_title, title, other_titles, connect, add_time,
                        user_id, latitude, longitude, height,
                        level_winter, level_summer, level_autumn, level_spring,
                        raw_data, images
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """, (
                    pereval_data.get('beauty_title', ''),
                    pereval_data['title'],
                    pereval_data.get('other_titles', ''),
                    pereval_data.get('connect', ''),
                    add_time,
                    user_id,
                    float(pereval_data['coords']['latitude']),
                    float(pereval_data['coords']['longitude']),
                    int(pereval_data['coords']['height']),
                    pereval_data.get('level', {}).get('winter', ''),
                    pereval_data.get('level', {}).get('summer', ''),
                    pereval_data.get('level', {}).get('autumn', ''),
                    pereval_data.get('level', {}).get('spring', ''),
                    json.dumps(pereval_data, ensure_ascii=False),
                    json.dumps(pereval_data.get('images', []), ensure_ascii=False)
                ))
                
                pereval_id = cursor.fetchone()['id']
                self.connection.commit()
                logger.info(f"Добавлен перевал с ID: {pereval_id}")
                return pereval_id
                
        except psycopg2.Error as e:
            logger.error(f"Ошибка при добавлении перевала: {e}")
            self.connection.rollback()
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Ошибка в данных перевала: {e}")
            return None
    
    def get_pereval_by_id(self, pereval_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение данных о перевале по ID
        
        Args:
            pereval_id: ID перевала
            
        Returns:
            Dict: Данные о перевале или None
        """
        if not self.connection:
            return None
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, u.email, u.phone, u.fam, u.name, u.otc
                    FROM pereval_added p
                    JOIN pereval_users u ON p.user_id = u.id
                    WHERE p.id = %s
                """, (pereval_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except psycopg2.Error as e:
            logger.error(f"Ошибка при получении перевала: {e}")
            return None
    
    def update_pereval(self, pereval_id: int, pereval_data: dict) -> dict:
        """
        Обновление существующего перевала
        
        Args:
            pereval_id: ID перевала для обновления
            pereval_data: Новые данные о перевале
            
        Returns:
            Dict: Результат обновления с state и message
        """
        if not self.connection:
            return {"state": 0, "message": "Нет подключения к базе данных"}
        
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, существует ли перевал и его статус
                cursor.execute("""
                    SELECT status FROM pereval_added WHERE id = %s
                """, (pereval_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {"state": 0, "message": f"Перевал с ID {pereval_id} не найден"}
                
                if result['status'] != 'new':
                    return {"state": 0, "message": f"Перевал с ID {pereval_id} уже был обработан модератором"}
                
                # Подготавливаем данные для обновления
                add_time = None
                if pereval_data.get('add_time'):
                    try:
                        from datetime import datetime
                        add_time = datetime.strptime(pereval_data['add_time'], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        add_time = datetime.now()
                else:
                    from datetime import datetime
                    add_time = datetime.now()
                
                # Обновляем данные о перевале
                import json
                cursor.execute("""
                    UPDATE pereval_added SET
                        beauty_title = %s,
                        title = %s,
                        other_titles = %s,
                        connect = %s,
                        add_time = %s,
                        latitude = %s,
                        longitude = %s,
                        height = %s,
                        level_winter = %s,
                        level_summer = %s,
                        level_autumn = %s,
                        level_spring = %s,
                        raw_data = %s,
                        images = %s
                    WHERE id = %s
                """, (
                    pereval_data.get('beauty_title', ''),
                    pereval_data['title'],
                    pereval_data.get('other_titles', ''),
                    pereval_data.get('connect', ''),
                    add_time,
                    float(pereval_data['coords']['latitude']),
                    float(pereval_data['coords']['longitude']),
                    int(pereval_data['coords']['height']),
                    pereval_data.get('level', {}).get('winter', ''),
                    pereval_data.get('level', {}).get('summer', ''),
                    pereval_data.get('level', {}).get('autumn', ''),
                    pereval_data.get('level', {}).get('spring', ''),
                    json.dumps(pereval_data, ensure_ascii=False),
                    json.dumps(pereval_data.get('images', []), ensure_ascii=False),
                    pereval_id
                ))
                
                self.connection.commit()
                logger.info(f"Обновлен перевал с ID: {pereval_id}")
                return {"state": 1, "message": "Запись успешно обновлена"}
                
        except psycopg2.Error as e:
            logger.error(f"Ошибка при обновлении перевала: {e}")
            self.connection.rollback()
            return {"state": 0, "message": f"Ошибка базы данных: {str(e)}"}
        except (ValueError, KeyError) as e:
            logger.error(f"Ошибка в данных перевала: {e}")
            return {"state": 0, "message": f"Ошибка в данных: {str(e)}"}
    
    def update_pereval_status(self, pereval_id: int, status: str) -> bool:
        """
        Обновление статуса модерации перевала
        
        Args:
            pereval_id: ID перевала
            status: Новый статус ('new', 'pending', 'accepted', 'rejected')
            
        Returns:
            bool: True если обновление успешно
        """
        if not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE pereval_added 
                    SET status = %s 
                    WHERE id = %s
                """, (status, pereval_id))
                
                self.connection.commit()
                logger.info(f"Статус перевала {pereval_id} обновлен на {status}")
                return True
                
        except psycopg2.Error as e:
            logger.error(f"Ошибка при обновлении статуса: {e}")
            self.connection.rollback()
            return False
