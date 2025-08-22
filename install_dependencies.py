#!/usr/bin/env python3
"""
Скрипт для автоматической установки зависимостей улучшенного бэкдора.
"""

import subprocess
import sys
import os
import platform

def install_package(package):
    """Устанавливает пакет через pip."""
    try:
        print(f"📦 Установка {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} успешно установлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке {package}: {e}")
        return False

def install_requirements():
    """Устанавливает все необходимые зависимости."""
    print("🚀 Установка зависимостей для улучшенного бэкдора...")
    print(f"🐍 Python версия: {sys.version}")
    print(f"💻 ОС: {platform.system()} {platform.release()}")
    print()
    
    # Основные зависимости
    core_packages = [
        "requests>=2.28.0",
        "psutil>=5.9.0",
        "Pillow>=9.0.0"
    ]
    
    # Зависимости для веб-камеры
    webcam_packages = [
        "opencv-python>=4.6.0"
    ]
    
    # Зависимости для Linux
    linux_packages = [
        "netifaces>=0.11.0"
    ]
    
    # Зависимости для обфускации (опционально)
    optional_packages = [
        "pyarmor>=7.7.0",
        "cryptography>=3.4.0"
    ]
    
    success_count = 0
    total_count = 0
    
    # Устанавливаем основные зависимости
    print("🔧 Установка основных зависимостей...")
    for package in core_packages:
        total_count += 1
        if install_package(package):
            success_count += 1
        print()
    
    # Устанавливаем зависимости для веб-камеры
    print("📷 Установка зависимостей для веб-камеры...")
    for package in webcam_packages:
        total_count += 1
        if install_package(package):
            success_count += 1
        print()
    
    # Устанавливаем Linux зависимости
    if platform.system() == "Linux":
        print("🐧 Установка Linux зависимостей...")
        for package in linux_packages:
            total_count += 1
            if install_package(package):
                success_count += 1
            print()
    
    # Устанавливаем опциональные зависимости
    print("🔒 Установка опциональных зависимостей...")
    for package in optional_packages:
        total_count += 1
        if install_package(package):
            success_count += 1
        print()
    
    # Результаты
    print("📊 РЕЗУЛЬТАТЫ УСТАНОВКИ")
    print("=" * 40)
    print(f"✅ Успешно установлено: {success_count}")
    print(f"❌ Ошибок: {total_count - success_count}")
    print(f"📦 Всего пакетов: {total_count}")
    print(f"📈 Процент успеха: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 Все зависимости успешно установлены!")
        print("🚀 Бэкдор готов к использованию!")
    else:
        print(f"\n⚠️ Установлено {success_count}/{total_count} зависимостей")
        print("💡 Некоторые функции могут быть недоступны")
    
    return success_count == total_count

def check_dependencies():
    """Проверяет установленные зависимости."""
    print("🔍 Проверка установленных зависимостей...")
    print()
    
    dependencies = {
        "requests": "HTTP запросы",
        "psutil": "Системная информация", 
        "PIL": "Обработка изображений",
        "cv2": "Веб-камера (OpenCV)",
        "netifaces": "Сетевые интерфейсы (Linux)"
    }
    
    available = []
    missing = []
    
    for module, description in dependencies.items():
        try:
            if module == "PIL":
                import PIL
                available.append(f"✅ {module} - {description}")
            elif module == "cv2":
                import cv2
                available.append(f"✅ {module} - {description}")
            elif module == "netifaces":
                if platform.system() == "Linux":
                    import netifaces
                    available.append(f"✅ {module} - {description}")
                else:
                    available.append(f"ℹ️ {module} - {description} (только Linux)")
            else:
                __import__(module)
                available.append(f"✅ {module} - {description}")
        except ImportError:
            missing.append(f"❌ {module} - {description}")
    
    print("📋 СТАТУС ЗАВИСИМОСТЕЙ")
    print("=" * 40)
    
    for item in available:
        print(item)
    
    if missing:
        print()
        print("❌ ОТСУТСТВУЮЩИЕ ЗАВИСИМОСТИ:")
        for item in missing:
            print(item)
    
    return len(missing) == 0

def main():
    """Основная функция."""
    print("🚀 УСТАНОВЩИК ЗАВИСИМОСТЕЙ ДЛЯ УЛУЧШЕННОГО БЭКДОРА")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Только проверка
        check_dependencies()
    else:
        # Установка + проверка
        if install_requirements():
            print()
            check_dependencies()
        else:
            print("\n⚠️ Установка завершена с ошибками")
            print("💡 Попробуйте установить недостающие пакеты вручную")

if __name__ == "__main__":
    main()
