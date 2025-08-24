#!/usr/bin/env python3
"""
Скрипт для настройки отдельного Telegram бота для паролей
"""

import requests
import json
import sys
import os

def create_password_bot():
    """Инструкции по созданию отдельного бота для паролей."""
    print("🔐 Настройка отдельного бота для паролей")
    print("=" * 50)
    print()
    print("1. Создание бота:")
    print("   - Найдите @BotFather в Telegram")
    print("   - Отправьте команду /newbot")
    print("   - Выберите имя для бота (например: PasswordManagerBot)")
    print("   - Выберите username для бота (например: password_manager_bot)")
    print("   - Сохраните полученный токен")
    print()
    print("2. Настройка бота:")
    print("   - Отправьте /setdescription для установки описания")
    print("   - Отправьте /setabouttext для установки информации о боте")
    print("   - Рекомендуемое описание: 'Безопасный бот для управления паролями'")
    print()
    print("3. Добавление бота в чат:")
    print("   - Создайте приватный чат или канал")
    print("   - Добавьте бота в чат как администратора")
    print("   - Отправьте любое сообщение в чат")
    print()
    print("4. Получение ID чата:")
    print("   - Перейдите по ссылке:")
    print("   - https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("   - Найдите 'chat_id' в ответе")
    print()
    print("5. Обновление конфигурации:")
    print("   - Отредактируйте файл config.py")
    print("   - Установите PASSWORD_BOT_TOKEN и PASSWORD_CHAT_ID")
    print()

def test_bot_connection(token, chat_id):
    """Тестирует подключение к боту."""
    try:
        # Тестируем получение информации о боте
        url = f'https://api.telegram.org/bot{token}/getMe'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            bot_info = result.get("result", {})
            print(f"✅ Подключение к боту успешно!")
            print(f"   Имя: {bot_info.get('first_name', 'Unknown')}")
            print(f"   Username: @{bot_info.get('username', 'Unknown')}")
            print(f"   ID: {bot_info.get('id', 'Unknown')}")
        else:
            print(f"❌ Ошибка подключения к боту: {result.get('description', 'Unknown error')}")
            return False
        
        # Тестируем отправку сообщения
        test_message = "🧪 Тестовое сообщение от скрипта настройки"
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        params = {
            'chat_id': chat_id,
            'text': test_message
        }
        
        response = requests.post(url, data=params, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Тестовое сообщение отправлено в чат {chat_id}")
            return True
        else:
            print(f"❌ Ошибка отправки сообщения: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def update_config_file(token, chat_id):
    """Обновляет файл конфигурации."""
    try:
        config_path = 'config.py'
        
        if not os.path.exists(config_path):
            print(f"❌ Файл {config_path} не найден")
            return False
        
        # Читаем текущий файл
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем значения
        content = content.replace('PASSWORD_BOT_TOKEN = "YOUR_PASSWORD_BOT_TOKEN"', f'PASSWORD_BOT_TOKEN = "{token}"')
        content = content.replace('PASSWORD_CHAT_ID = "YOUR_PASSWORD_CHAT_ID"', f'PASSWORD_CHAT_ID = "{chat_id}"')
        
        # Записываем обновленный файл
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Файл {config_path} обновлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении конфигурации: {e}")
        return False

def main():
    """Основная функция."""
    print("🚀 Настройка отдельного бота для паролей")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        create_password_bot()
        return
    
    if len(sys.argv) == 3:
        token = sys.argv[1]
        chat_id = sys.argv[2]
        
        print(f"Токен бота: {token}")
        print(f"ID чата: {chat_id}")
        print()
        
        # Тестируем подключение
        if test_bot_connection(token, chat_id):
            # Обновляем конфигурацию
            if update_config_file(token, chat_id):
                print()
                print("🎉 Настройка завершена успешно!")
                print("Теперь пароли будут отправляться через отдельного бота")
                print()
                print("Для тестирования запустите:")
                print("python test_password_manager.py")
            else:
                print("❌ Ошибка при обновлении конфигурации")
        else:
            print("❌ Ошибка при тестировании бота")
            print("Проверьте токен и ID чата")
    else:
        print("Использование:")
        print("python setup_password_bot.py <BOT_TOKEN> <CHAT_ID>")
        print()
        print("Пример:")
        print("python setup_password_bot.py 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz -1001234567890")
        print()
        print("Для получения инструкций:")
        print("python setup_password_bot.py --help")

if __name__ == "__main__":
    main()
