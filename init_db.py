"""
Скрипт для инициализации базы данных
Создает таблицы и заполняет справочные данные
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


def init_database():
    """Инициализация базы данных"""
    
    # Параметры подключения
    host = os.getenv('FSTR_DB_HOST', 'localhost')
    port = os.getenv('FSTR_DB_PORT', '5432')
    login = os.getenv('FSTR_DB_LOGIN', 'postgres')
    password = os.getenv('FSTR_DB_PASS', 'password')
    database = os.getenv('FSTR_DB_NAME', 'pereval')
    
    try:
        # Подключаемся к PostgreSQL (к базе postgres для создания новой БД)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=login,
            password=password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Создаем базу данных если она не существует
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {database}")
            print(f"База данных {database} создана")
        else:
            print(f"База данных {database} уже существует")
        
        cursor.close()
        conn.close()
        
        # Подключаемся к созданной базе данных
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=login,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Читаем и выполняем SQL скрипт
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        cursor.execute(sql_script)
        conn.commit()
        
        print("Схема базы данных создана успешно")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Инициализация базы данных...")
    if init_database():
        print("База данных инициализирована успешно!")
    else:
        print("Ошибка при инициализации базы данных")
