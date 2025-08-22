import os
import sys
import uuid
import socket
import logging
import platform
import random
import time
import ctypes

from config import INSTANCE_ID_FILE, INSTANCE_NAME_FILE, INTERNET_CHECK_TIMEOUT

# Функция для проверки, предназначена ли команда для этого экземпляра
def is_command_for_this_instance(command: str, instance_id: str) -> bool:
    """Проверяет, предназначена ли команда для этого экземпляра.
    
    Args:
        command (str): Команда пользователя
        instance_id (str): ID текущего экземпляра
        
    Returns:
        bool: True если команда для этого экземпляра
    """
    try:
        # Разбираем команду на части
        parts = command.strip().split()
        if len(parts) < 2:
            # Команда без ID - для текущего экземпляра
            return True
        
        # Проверяем, является ли второй элемент ID
        target_id = parts[1]
        
        # Если ID совпадает с текущим экземпляром
        if target_id == instance_id:
            return True
        
        # Если ID не совпадает - команда не для этого экземпляра
        return False
        
    except Exception as e:
        logging.error(f"Ошибка при проверке команды: {e}")
        return True  # В случае ошибки обрабатываем команду

# Функция для очистки команды от ID экземпляра
def clean_command(command: str) -> str:
    """Убирает ID экземпляра из команды.
    
    Args:
        command (str): Команда с ID экземпляра
        
    Returns:
        str: Очищенная команда
    """
    try:
        parts = command.strip().split()
        if len(parts) >= 2:
            # Убираем ID экземпляра и возвращаем остальную часть команды
            return ' '.join(parts[2:]) if len(parts) > 2 else ""
        return command
    except Exception as e:
        logging.error(f"Ошибка при очистке команды: {e}")
        return command

# Функция для получения или создания уникального ID экземпляра
def get_or_create_instance_id() -> str:
    """Получает существующий ID экземпляра или создает новый.
    
    Returns:
        str: Уникальный ID экземпляра
    """
    try:
        # Пытаемся прочитать существующий ID
        if os.path.exists(INSTANCE_ID_FILE):
            with open(INSTANCE_ID_FILE, 'r') as f:
                instance_id = f.read().strip()
                if instance_id and len(instance_id) == 32:  # Проверяем валидность
                    logging.info(f"Найден существующий ID экземпляра: {instance_id}")
                    return instance_id
        
        # Создаем новый уникальный ID
        instance_id = uuid.uuid4().hex
        logging.info(f"Создан новый ID экземпляра: {instance_id}")
        
        # Сохраняем ID в файл
        try:
            with open(INSTANCE_ID_FILE, 'w') as f:
                f.write(instance_id)
            logging.info(f"ID экземпляра сохранен в {INSTANCE_ID_FILE}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении ID экземпляра: {e}")
        
        return instance_id
    except Exception as e:
        logging.error(f"Ошибка при получении/создании ID экземпляра: {e}")
        # Возвращаем fallback ID
        return f"fallback_{uuid.uuid4().hex[:16]}"

# Функция для получения или создания имени экземпляра
def get_or_create_instance_name() -> str:
    """Получает существующее имя экземпляра или создает новое.
    
    Returns:
        str: Имя экземпляра
    """
    try:
        # Пытаемся прочитать существующее имя
        if os.path.exists(INSTANCE_NAME_FILE):
            with open(INSTANCE_NAME_FILE, 'r') as f:
                instance_name = f.read().strip()
                if instance_name:
                    logging.info(f"Найден существующий имя экземпляра: {instance_name}")
                    return instance_name
        
        # Создаем новое имя на основе информации о системе
        try:
            hostname = socket.gethostname()
            username = os.getlogin()
            instance_name = f"{hostname}_{username}_{random.randint(1000, 9999)}"
        except:
            instance_name = f"Unknown_{random.randint(10000, 99999)}"
        
        logging.info(f"Создано новое имя экземпляра: {instance_name}")
        
        # Сохраняем имя в файл
        try:
            with open(INSTANCE_NAME_FILE, 'w') as f:
                f.write(instance_name)
            logging.info(f"Имя экземпляра сохранено в {INSTANCE_NAME_FILE}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении имени экземпляра: {e}")
        
        return instance_name
    except Exception as e:
        logging.error(f"Ошибка при получении/создании имени экземпляра: {e}")
        return f"Error_{random.randint(10000, 99999)}"

# Функция для проверки интернет-соединения
def check_internet_connection() -> bool:
    """Проверяет наличие интернет-соединения.
    
    Returns:
        bool: True если интернет доступен, иначе False
    """
    try:
        # Пробуем подключиться к Google DNS
        socket.create_connection(("8.8.8.8", 53), timeout=INTERNET_CHECK_TIMEOUT)
        return True
    except OSError:
        return False

# Функция для проверки успешности обновления
def verify_update_success() -> bool:
    """Проверяет, успешно ли прошло обновление."""
    try:
        # Проверяем, что текущий файл не старше 5 минут
        current_script = os.path.abspath(sys.argv[0])
        file_time = os.path.getmtime(current_script)
        if time.time() - file_time < 300:  # 5 минут
            return True
        return False
    except:
        return False


