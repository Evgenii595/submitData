#!/bin/bash

# Скрипт для запуска ФСТР API
echo "🚀 Запуск ФСТР API..."

# Установка переменных окружения
export FSTR_DB_HOST=127.0.0.1
export FSTR_DB_PORT=5432
export FSTR_DB_LOGIN=pereval_user
export FSTR_DB_PASS=password
export FSTR_DB_NAME=pereval

# Проверка подключения к PostgreSQL
echo "📊 Проверка подключения к PostgreSQL..."
if ! PGPASSWORD=password psql -h 127.0.0.1 -U pereval_user -d pereval -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Ошибка подключения к PostgreSQL. Убедитесь, что:"
    echo "   1. PostgreSQL запущен"
    echo "   2. Пользователь pereval_user создан с паролем password"
    echo "   3. База данных pereval существует"
    exit 1
fi

echo "✅ PostgreSQL подключен успешно"

# Запуск API
echo "🌐 Запуск API сервера..."
python3 main.py
