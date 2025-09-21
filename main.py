#!/usr/bin/env python3
"""
Главный файл для запуска системы уведомлений о здоровье
Health Notification System - Main Entry Point
"""

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def create_tables():
    """Создание таблиц базы данных"""
    with app.app_context():
        db.create_all()
        print("✅ Таблицы базы данных созданы успешно!")

def main():
    """Главная функция запуска"""
    print("🏥 Система уведомлений о здоровье для беременных женщин")
    print("=" * 60)
    
    # Создаем приложение Flask
    global app
    app = create_app()
    
    # Инициализируем базу данных
    with app.app_context():
        try:
            create_tables()
        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")
            print("Убедитесь, что MySQL запущен и настройки в .env корректны")
            return
    
    # Настройки запуска
    debug_mode = app.config.get('DEBUG', False)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n🚀 Запуск сервера на порту {port}")
    print(f"🔧 Режим отладки: {'Включен' if debug_mode else 'Выключен'}")
    print("\n📋 Доступные API endpoints:")
    print("  POST /api/patients                    - Создать пациента")
    print("  GET  /api/patients/{id}               - Получить пациента")
    print("  PUT  /api/patients/{id}               - Обновить пациента")
    print("  POST /api/assess-risk/{id}            - Оценить риск")
    print("  GET  /api/risk/{id}                   - Получить оценку риска")
    print("  GET  /api/notifications/{id}          - Получить уведомления")
    print("  GET  /api/health                      - Проверка системы")
    print("  GET  /api/weather/{zip}               - Данные о погоде")
    print("  GET  /api/weather-onecall/{zip}       - Comprehensive weather data (OneCall API)")
    print("  GET  /api/weather-forecast/{zip}      - Прогноз погоды")
    print("  GET  /api/weather-alerts/{zip}        - Погодные предупреждения")
    print("  GET  /api/weather-ai-analysis/{zip}   - AI анализ погодных рисков")
    print("  GET  /api/environment-metrics         - Метрики условий окружающей среды")
    print("  GET  /api/environment-metrics/{zip}   - Метрики по локации")
    print("  GET  /api/risk-patients               - Пациенты с рисками")
    print("  GET  /api/risk-patients/{id}          - Детали риска пациента")
    print("  GET  /api/risk-patients/{id}/comprehensive - Комплексная оценка риска")
    print("  GET  /api/risk-patients/summary       - Сводка по рискам")
    print("\n🌐 Откройте браузер: http://localhost:5000/api/health")
    print("=" * 60)
    
    # Запускаем приложение
    try:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")

if __name__ == '__main__':
    main()
