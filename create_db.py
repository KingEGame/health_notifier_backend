#!/usr/bin/env python3
"""
Скрипт для создания базы данных SQLite
"""

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменную окружения для SQLite
os.environ['USE_SQLITE'] = 'true'

from app import create_app, db

def create_database():
    """Создание базы данных SQLite"""
    print("🔧 Создание базы данных SQLite...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Создаем все таблицы
            db.create_all()
            print("✅ База данных SQLite создана успешно!")
            print(f"📁 Файл базы данных: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Проверяем, что таблицы созданы
            from app.models import Patient
            print(f"📊 Таблица Patient создана: {Patient.__tablename__}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании базы данных: {e}")
            return False
    
    return True

if __name__ == '__main__':
    create_database()
