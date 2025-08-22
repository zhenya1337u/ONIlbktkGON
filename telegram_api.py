import requests
import urllib.parse
import json
import logging
from typing import Dict, Any
import platform
import os

from config import BOT_TOKEN, CHAT_ID

# Функция для отправки текста в Telegram
def send_text_to_telegram(message: str) -> Dict[str, Any]:
    """Отправляет текстовое сообщение в Telegram чат.
    
    Args:
        message (str): Текст для отправки
        
    Returns:
        Dict[str, Any]: Результат отправки сообщения
    """
    logging.info(f"Отправка сообщения в Telegram (длина: {len(message)} символов)")
    
    # Ограничиваем длину сообщения, чтобы избежать ошибок API
    max_length = 4000
    if len(message) > max_length:
        message = message[:max_length-100] + "\n\n[Сообщение слишком длинное и было обрезано...]"
    
    try:
        # Пробуем отправить через requests
        try:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            params = {
                'chat_id': CHAT_ID, 
                'text': message,
                'parse_mode': 'HTML'  # Поддержка HTML форматирования
            }
            response = requests.post(url, data=params, timeout=10)
            result = response.json()
            if result.get("ok"):
                logging.info("Сообщение успешно отправлено")
            else:
                logging.error(f"Ошибка при отправке сообщения: {result}")
            return result
        except Exception as e:
            logging.error(f"Ошибка при отправке через requests: {e}")
            
        # Если requests не сработал, пробуем через urllib
        try:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message}).encode('utf-8')
            req = urllib.request.Request(url, data=data, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                logging.info("Сообщение успешно отправлено через urllib")
                return response_data
        except Exception as e2:
            logging.error(f"Ошибка при отправке через urllib: {e2}")
            return {"ok": False, "error": str(e2)}
            
        return {"ok": False}
    except Exception as e3:
        logging.error(f"Критическая ошибка при отправке сообщения: {e3}")
        return {"ok": False, "error": str(e3)}

# Функция для очистки ожидающих обновлений
def clear_pending_updates() -> int:
    """Очищает очередь ожидающих обновлений Telegram.
    
    Returns:
        int: ID последнего обновления
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            updates = response.json()
            if updates.get("ok") and updates.get("result"):
                # Получаем ID последнего обновления
                last_update_id = updates["result"][-1]["update_id"]
                
                # Очищаем очередь, запросив обновления с offset = last_update_id + 1
                clear_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}"
                requests.get(clear_url, timeout=10)
                
                logging.info(f"Очищена очередь обновлений, последний ID: {last_update_id}")
                return last_update_id
            else:
                logging.info("Очередь обновлений пуста")
                return 0
        else:
            logging.error(f"Ошибка при очистке очереди: HTTP {response.status_code}")
            return 0
    except Exception as e:
        logging.error(f"Ошибка при очистке ожидающих обновлений: {e}")
        return 0

# Функция для отправки фото в Telegram
def send_photo_to_telegram(photo_path: str, caption: str = "") -> Dict[str, Any]:
    """Отправляет фото в Telegram чат.
    
    Args:
        photo_path (str): Путь к файлу фото
        caption (str): Подпись к фото
        
    Returns:
        Dict[str, Any]: Результат отправки фото
    """
    logging.info(f"Отправка фото в Telegram: {photo_path}")
    
    try:
        if not os.path.exists(photo_path):
            logging.error(f"Файл фото не найден: {photo_path}")
            return {"ok": False, "error": "File not found"}
        
        # Проверяем размер файла (максимум 10 MB для фото)
        file_size = os.path.getsize(photo_path)
        if file_size > 10 * 1024 * 1024:
            logging.error(f"Файл фото слишком большой: {file_size} байт")
            return {"ok": False, "error": "File too large"}
        
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
        
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()
            
            if result.get("ok"):
                logging.info("Фото успешно отправлено")
            else:
                logging.error(f"Ошибка при отправке фото: {result}")
            
            return result
            
    except Exception as e:
        logging.error(f"Ошибка при отправке фото: {e}")
        return {"ok": False, "error": str(e)}

# Функция для отправки файла в Telegram
def send_file_to_telegram(file_path: str, caption: str = "") -> Dict[str, Any]:
    """Отправляет файл в Telegram чат.
    
    Args:
        file_path (str): Путь к файлу для отправки
        caption (str): Подпись к файлу
        
    Returns:
        Dict[str, Any]: Результат отправки файла
    """
    logging.info(f"Отправка файла в Telegram: {file_path}")
    
    try:
        if not os.path.exists(file_path):
            logging.error(f"Файл не найден: {file_path}")
            return {"ok": False, "error": "File not found"}
        
        # Проверяем размер файла (максимум 50 MB для файлов)
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            logging.error(f"Файл слишком большой: {file_size} байт")
            return {"ok": False, "error": "File too large"}
        
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
        
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {
                'chat_id': CHAT_ID,
                'caption': caption
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
            result = response.json()
            
            if result.get("ok"):
                logging.info("Файл успешно отправлен")
            else:
                logging.error(f"Ошибка при отправке файла: {result}")
            
            return result
            
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")
        return {"ok": False, "error": str(e)}



