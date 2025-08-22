import platform
import socket
import psutil
import uuid
import ctypes
import logging
import os
from datetime import datetime
from typing import Dict, Any

from utils import get_or_create_instance_id, get_or_create_instance_name

# Функция для получения информации о системе
def get_system_info() -> Dict[str, Any]:
    """Собирает информацию о системе пользователя.
    
    Returns:
        Dict[str, Any]: Словарь с информацией о системе или сообщение об ошибке
    """
    try:
        logging.info("Сбор информации о системе")
        
        # Получаем ID и имя экземпляра
        instance_id = get_or_create_instance_id()
        instance_name = get_or_create_instance_name()
        
        username = "Unknown"
        try:
            username = os.getlogin()
        except OSError as e:
            logging.warning(f"Ошибка при получении имени пользователя через os.getlogin(): {e}. Попытка использовать переменные окружения.")
            username = os.environ.get("USER") or os.environ.get("USERNAME") or "Unknown"

        ip_address = "N/A"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except Exception as e:
            logging.warning(f"Ошибка при получении IP-адреса через сокет: {e}. Попытка использовать gethostname.")
            try:
                ip_address = socket.gethostbyname(socket.gethostname())
            except Exception as e_hostname:
                logging.warning(f"Ошибка при получении IP-адреса через gethostname: {e_hostname}")
                ip_address = "N/A"

        mac_address = "N/A"
        try:
            # For Linux, try to get MAC address from network interfaces
            if platform.system() == "Linux":
                import netifaces
                for interface in netifaces.interfaces():
                    try:
                        if netifaces.AF_LINK in netifaces.ifaddresses(interface):
                            mac_address = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]["addr"]
                            break
                    except Exception as e:
                        logging.warning(f"Ошибка при получении MAC-адреса для интерфейса {interface}: {e}")
            else:
                mac_address = ":".join([f"{((uuid.getnode() >> elements) & 0xff):02x}" for elements in range(0, 48, 8)][::-1])
        except Exception as e:
            logging.warning(f"Ошибка при получении MAC-адреса: {e}")
            mac_address = "N/A"

        is_admin = False
        try:
            if platform.system() == "Windows":
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            else:
                is_admin = (os.geteuid() == 0)
        except Exception as e:
            logging.warning(f"Ошибка при проверке прав администратора: {e}")
            is_admin = False

        info = {
            "instance_id": instance_id,
            "instance_name": instance_name,
            "hostname": socket.gethostname(),
            "ip": ip_address,
            "os": platform.system(),
            "os_version": platform.version(),
            "username": username,
            "machine": platform.machine(),
            "processor": platform.processor(),
            "ram": f"{round(psutil.virtual_memory().total / (1024.0 ** 3), 2)} GB",
            "mac_address": mac_address,
            "admin": is_admin,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Добавляем информацию о дисках
        disks = []
        try:
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total": f"{round(usage.total / (1024.0 ** 3), 2)} GB",
                        "used": f"{round(usage.used / (1024.0 ** 3), 2)} GB",
                        "free": f"{round(usage.free / (1024.0 ** 3), 2)} GB",
                        "percent": f"{usage.percent}%"
                    })
                except Exception as e:
                    logging.warning(f"Ошибка при сборе информации о диске {part.mountpoint}: {e}")
        except Exception as e:
            logging.warning(f"Ошибка при получении списка дисков: {e}")
        info["disks"] = disks
        
        logging.info("Информация о системе собрана успешно")
        return info
    except Exception as e:
        logging.error(f"Ошибка при сборе информации о системе: {e}")
        return {"error": str(e)}

def format_system_info(info: Dict[str, Any]) -> str:
    """Форматирует информацию о системе в красивом HTML виде.
    
    Args:
        info (Dict[str, Any]): Словарь с информацией о системе
        
    Returns:
        str: Отформатированная HTML строка
    """
    try:
        html = f"""💻 <b>ИНФОРМАЦИЯ О СИСТЕМЕ</b>

🆔 <b>Экземпляр:</b> <code>{info.get("instance_id", "N/A")}</code>
📝 <b>Имя:</b> <code>{info.get("instance_name", "N/A")}</code>

🖥️ <b>ОС</b>
├─ <b>Тип:</b> {info.get("os", "N/A")} {info.get("os_version", "")}
├─ <b>Архитектура:</b> {info.get("machine", "N/A")}
├─ <b>Процессор:</b> {info.get("processor", "N/A")}
└─ <b>RAM:</b> {info.get("ram", "N/A")}

🌐 <b>СЕТЬ</b>
├─ <b>Hostname:</b> <code>{info.get("hostname", "N/A")}</code>
├─ <b>IP адрес:</b> <code>{info.get("ip", "N/A")}</code>
└─ <b>MAC адрес:</b> <code>{info.get("mac_address", "N/A")}</code>

👤 <b>ПОЛЬЗОВАТЕЛЬ</b>
├─ <b>Имя:</b> <code>{info.get("username", "N/A")}</code>
└─ <b>Права админа:</b> {"✅ Да" if info.get("admin", False) else "❌ Нет"}"""
        
        # Добавляем информацию о дисках
        if "disks" in info and info["disks"]:
            html += "\n\n💾 <b>ДИСКИ</b>"
            for i, disk in enumerate(info["disks"]):
                if i == len(info["disks"]) - 1:
                    prefix = "└─"
                else:
                    prefix = "├─"
                
                # Определяем цвет для процента использования
                percent = float(disk.get("percent", "0%").replace("%", ""))
                if percent > 90:
                    percent_color = "🔴"
                elif percent > 70:
                    percent_color = "🟡"
                else:
                    percent_color = "🔵"
                
                device_name = disk.get("device")
                fstype = disk.get("fstype")
                mountpoint = disk.get("mountpoint")
                total = disk.get("total")
                used = disk.get("used")
                free = disk.get("free")
                percent = disk.get("percent")
                
                html += f"\n{prefix} <b>{device_name}</b> ({fstype})"
                html += f"\n    📁 {mountpoint}"
                html += f"\n    💿 {total} | {used} | {free}"
                html += f"\n    {percent_color} Использовано: {percent}"
        
        # Добавляем статус
        html += f"\n\n✅ <b>СТАТУС:</b> <code>Активен</code>"
        
        return html
        
    except Exception as e:
        logging.error(f"Ошибка при форматировании информации: {e}")
        return f"❌ <b>Ошибка при форматировании:</b>\n<code>{str(e)}</code>"


