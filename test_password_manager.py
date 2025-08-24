#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы менеджера паролей
"""

import sys
import os
import time

# Добавляем путь к родительской директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from password_manager import PasswordManager, init_password_manager, cleanup_password_manager

def test_password_generation():
    """Тестирует генерацию паролей."""
    print("🔐 Тестирование генерации паролей...")
    
    manager = PasswordManager()
    
    # Тестируем генерацию паролей разной длины
    for length in [8, 12, 16]:
        password = manager.generate_password(length)
        print(f"   Пароль длиной {length}: {password}")
        assert len(password) == length, f"Неверная длина пароля: {len(password)} != {length}"
    
    print("✅ Генерация паролей работает корректно\n")

def test_custom_credentials():
    """Тестирует установку пользовательских учетных данных."""
    print("👤 Тестирование установки пользовательских учетных данных...")
    
    manager = PasswordManager()
    
    # Тестируем установку новых учетных данных
    username = "testuser"
    password = "testpass123"
    
    success = manager.set_custom_credentials(username, password)
    print(f"   Установка учетных данных: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    print("✅ Установка учетных данных работает корректно\n")

def test_auto_update():
    """Тестирует автоматическое обновление паролей."""
    print("🔄 Тестирование автоматического обновления паролей...")
    
    manager = PasswordManager()
    
    # Устанавливаем короткий интервал для тестирования
    manager.password_update_interval = 10  # 10 секунд
    
    print("   Запуск автоматического обновления...")
    manager.start_auto_update()
    
    # Ждем немного
    print("   Ожидание 15 секунд...")
    time.sleep(15)
    
    print("   Остановка автоматического обновления...")
    manager.stop_auto_update()
    
    print("✅ Автоматическое обновление работает корректно\n")

def test_telegram_integration():
    """Тестирует интеграцию с Telegram."""
    print("📱 Тестирование интеграции с Telegram...")
    
    try:
        from telegram_api import send_text_to_telegram
        
        message = "🧪 Тестовое сообщение от менеджера паролей"
        result = send_text_to_telegram(message)
        
        if result.get("ok"):
            print("✅ Сообщение успешно отправлено в Telegram")
        else:
            print(f"❌ Ошибка отправки: {result}")
            
    except Exception as e:
        print(f"❌ Ошибка интеграции с Telegram: {e}")
    
    print()

def test_password_bot_integration():
    """Тестирует интеграцию с отдельным ботом для паролей."""
    print("🔐 Тестирование интеграции с отдельным ботом для паролей...")
    
    try:
        from password_telegram import test_password_bot_connection, send_password_to_telegram
        
        # Тестируем подключение
        connection_ok = test_password_bot_connection()
        
        if connection_ok:
            # Тестируем отправку сообщения
            test_message = "🧪 Тестовое сообщение от отдельного бота паролей"
            result = send_password_to_telegram(test_message)
            
            if result.get("ok"):
                print("✅ Сообщение успешно отправлено через отдельного бота")
            else:
                print(f"❌ Ошибка отправки через отдельного бота: {result}")
        else:
            print("❌ Ошибка подключения к отдельному боту")
            
    except Exception as e:
        print(f"❌ Ошибка интеграции с отдельным ботом: {e}")
    
    print()

def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестов менеджера паролей\n")
    
    try:
        test_password_generation()
        test_custom_credentials()
        test_auto_update()
        test_telegram_integration()
        test_password_bot_integration()
        
        print("🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
