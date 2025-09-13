"""
Тестовый скрипт для проверки работы API
Отправляет тестовые данные на endpoint submitData
"""

import requests
import json
from datetime import datetime

# URL API (измените если запускаете на другом порту)
API_URL = "http://localhost:8000"

def test_submit_data():
    """Тест отправки данных о перевале"""
    
    # Тестовые данные
    test_data = {
        "beauty_title": "пер. ",
        "title": "Тестовый перевал",
        "other_titles": "Тест",
        "connect": "Соединяет долины",
        "add_time": "2024-01-15 10:30:00",
        "user": {
            "email": "test@example.com",
            "fam": "Тестов",
            "name": "Иван",
            "otc": "Петрович",
            "phone": "+7 999 123 45 67"
        },
        "coords": {
            "latitude": "45.3842",
            "longitude": "7.1525",
            "height": "1200"
        },
        "level": {
            "winter": "",
            "summer": "1А",
            "autumn": "1А",
            "spring": ""
        },
        "images": [
            {"data": "base64_encoded_image_data_1", "title": "Седловина"},
            {"data": "base64_encoded_image_data_2", "title": "Подъём"}
        ]
    }
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            f"{API_URL}/submitData",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус HTTP: {response.status_code}")
        print(f"Ответ сервера: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Тест прошел успешно!")
            return response.json().get('id')
        else:
            print("❌ Тест не прошел")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения. Убедитесь, что API запущен на localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def test_health_check():
    """Тест проверки состояния API"""
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Health check статус: {response.status_code}")
        print(f"Ответ: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check прошел успешно!")
            return True
        else:
            print("❌ Health check не прошел")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка health check: {e}")
        return False


def test_get_pereval(pereval_id):
    """Тест получения данных о перевале"""
    
    try:
        response = requests.get(f"{API_URL}/pereval/{pereval_id}")
        print(f"GET pereval статус: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Получение данных о перевале успешно!")
            print(f"Данные: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ Ошибка получения данных: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка получения данных: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Запуск тестов API...")
    print("=" * 50)
    
    # Тест 1: Health check
    print("\n1. Тест health check:")
    health_ok = test_health_check()
    
    if not health_ok:
        print("❌ API недоступен. Завершение тестов.")
        exit(1)
    
    # Тест 2: Отправка данных
    print("\n2. Тест отправки данных о перевале:")
    pereval_id = test_submit_data()
    
    if pereval_id:
        # Тест 3: Получение данных
        print(f"\n3. Тест получения данных о перевале (ID: {pereval_id}):")
        test_get_pereval(pereval_id)
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено!")
