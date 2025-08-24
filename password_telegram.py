#!/usr/bin/env python3
"""
Модуль для отправки паролей через отдельного Telegram бота
Обеспечивает дополнительную безопасность и изоляцию
"""

import requests
import urllib.parse
import json
import logging
from typing import Dict, Any
from datetime import datetime

from config import PASSWORD_BOT_TOKEN, PASSWORD_CHAT_ID

logger = logging.getLogger(__name__)

def send_password_to_telegram(message: str) -> Dict[str, Any]:
    """Отправляет сообщение с паролем через отдельного бота.
    
    Args:
        message (str): Текст сообщения с паролем
        
    Returns:
        Dict[str, Any]: Результат отправки сообщения
    """
    logging.info(f"Отправка пароля через отдельного бота (длина: {len(message)} символов)")
    
    # Ограничиваем длину сообщения
    max_length = 4000
    if len(message) > max_length:
        message = message[:max_length-100] + "\n\n[Сообщение слишком длинное и было обрезано...]"
    
    try:
        # Проверяем, настроен ли отдельный бот
        if PASSWORD_BOT_TOKEN == "YOUR_PASSWORD_BOT_TOKEN" or PASSWORD_CHAT_ID == "YOUR_PASSWORD_CHAT_ID":
            logger.warning("Отдельный бот для паролей не настроен, используем основной бот")
            return send_password_fallback(message)
        
        # Отправляем через отдельного бота
        url = f'https://api.telegram.org/bot{PASSWORD_BOT_TOKEN}/sendMessage'
        params = {
            'chat_id': PASSWORD_CHAT_ID, 
            'text': message,
            'parse_mode': 'HTML'  # Поддержка HTML форматирования
        }
        
        response = requests.post(url, data=params, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            logger.info("Пароль успешно отправлен через отдельного бота")
        else:
            logger.error(f"Ошибка при отправке пароля через отдельного бота: {result}")
            # Пробуем через основной бот как резервный вариант
            return send_password_fallback(message)
            
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при отправке пароля через отдельного бота: {e}")
        # Пробуем через основной бот как резервный вариант
        return send_password_fallback(message)

def send_password_fallback(message: str) -> Dict[str, Any]:
    """Резервная отправка пароля через основной бот."""
    try:
        from telegram_api import send_text_to_telegram
        logger.info("Используем основной бот как резервный вариант")
        return send_text_to_telegram(message)
    except Exception as e:
        logger.error(f"Ошибка при резервной отправке пароля: {e}")
        return {"ok": False, "error": str(e)}

def send_new_password_notification(username: str, password: str, update_interval: int = 300) -> bool:
    """Отправляет уведомление о новом пароле.
    
    Args:
        username (str): Имя пользователя
        password (str): Новый пароль
        update_interval (int): Интервал обновления в секундах
        
    Returns:
        bool: True если отправка успешна
    """
    try:
        message = f"""
🔐 **НОВЫЙ ПАРОЛЬ АДМИНИСТРАТОРА**

📅 Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 Пользователь: {username}
🔑 Новый пароль: `{password}`
🌐 Панель управления: http://localhost:5000

⚠️ Пароль будет обновлен через {update_interval // 60} минут!

🔒 Отправлено через защищенного бота
        """
        
        result = send_password_to_telegram(message)
        return result.get("ok", False)
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления о пароле: {e}")
        return False

def send_custom_credentials_notification(username: str, password: str) -> bool:
    """Отправляет уведомление о пользовательских учетных данных.
    
    Args:
        username (str): Имя пользователя
        password (str): Пароль
        
    Returns:
        bool: True если отправка успешна
    """
    try:
        message = f"""
👤 **ПОЛЬЗОВАТЕЛЬСКИЕ УЧЕТНЫЕ ДАННЫЕ**

📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
✅ Пользователь создан/обновлен: {username}
🔑 Пароль: `{password}`
🌐 Панель управления: http://localhost:5000

🔒 Отправлено через защищенного бота
        """
        
        result = send_password_to_telegram(message)
        return result.get("ok", False)
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления об учетных данных: {e}")
        return False

def test_password_bot_connection() -> bool:
    """Тестирует подключение к отдельному боту для паролей.
    
    Returns:
        bool: True если подключение успешно
    """
    try:
        if PASSWORD_BOT_TOKEN == "YOUR_PASSWORD_BOT_TOKEN" or PASSWORD_CHAT_ID == "YOUR_PASSWORD_CHAT_ID":
            logger.warning("Отдельный бот для паролей не настроен")
            return False
        
        url = f'https://api.telegram.org/bot{PASSWORD_BOT_TOKEN}/getMe'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            bot_info = result.get("result", {})
            logger.info(f"Подключение к боту паролей успешно: @{bot_info.get('username', 'Unknown')}")
            return True
        else:
            logger.error(f"Ошибка подключения к боту паролей: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при тестировании подключения к боту паролей: {e}")
        return False

def get_password_bot_status() -> Dict[str, Any]:
    """Получает статус бота для паролей.
    
    Returns:
        Dict[str, Any]: Информация о статусе бота
    """
    try:
        if PASSWORD_BOT_TOKEN == "YOUR_PASSWORD_BOT_TOKEN":
            return {
                "configured": False,
                "message": "Отдельный бот для паролей не настроен"
            }
        
        url = f'https://api.telegram.org/bot{PASSWORD_BOT_TOKEN}/getMe'
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get("ok"):
            bot_info = result.get("result", {})
            return {
                "configured": True,
                "bot_name": bot_info.get("first_name", "Unknown"),
                "bot_username": bot_info.get("username", "Unknown"),
                "chat_id": PASSWORD_CHAT_ID
            }
        else:
            return {
                "configured": False,
                "message": f"Ошибка подключения: {result.get('description', 'Unknown error')}"
            }
            
    except Exception as e:
        return {
            "configured": False,
            "message": f"Ошибка: {str(e)}"
        }
