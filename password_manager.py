#!/usr/bin/env python3
"""
Модуль управления паролями для веб-панели
Автоматическое обновление пароля каждые 5 минут
"""

import secrets
import string
import threading
import time
import logging
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from password_telegram import send_new_password_notification, send_custom_credentials_notification
from config import BOT_TOKEN, CHAT_ID

logger = logging.getLogger(__name__)

class PasswordManager:
    def __init__(self, db_path='web_dashboard/devices.db'):
        self.db_path = db_path
        self.password_update_interval = 300  # 5 минут
        self.password_length = 12
        self.is_running = False
        self.update_thread = None
        
    def generate_password(self, length=12):
        """Генерирует случайный пароль заданной длины."""
        # Используем буквы, цифры и специальные символы
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def update_admin_password(self):
        """Обновляет пароль администратора и отправляет в Telegram."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Генерируем новый пароль
            new_password = self.generate_password(self.password_length)
            password_hash = generate_password_hash(new_password)
            
            # Обновляем пароль в базе данных
            cursor.execute('''
                UPDATE users 
                SET password_hash = ? 
                WHERE username = "admin"
            ''', (password_hash,))
            
            conn.commit()
            conn.close()
            
            # Отправляем новый пароль через отдельного бота
            success = send_new_password_notification("admin", new_password, self.password_update_interval)
            if success:
                logger.info(f"Пароль обновлен и отправлен через отдельного бота: {new_password}")
            else:
                logger.error("Ошибка отправки пароля через отдельного бота")
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении пароля: {e}")
    
    def start_auto_update(self):
        """Запускает автоматическое обновление пароля."""
        if self.is_running:
            logger.warning("Автоматическое обновление пароля уже запущено")
            return
            
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("Автоматическое обновление пароля запущено")
    
    def stop_auto_update(self):
        """Останавливает автоматическое обновление пароля."""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        logger.info("Автоматическое обновление пароля остановлено")
    
    def _update_loop(self):
        """Основной цикл обновления пароля."""
        while self.is_running:
            try:
                # Ждем указанный интервал
                time.sleep(self.password_update_interval)
                
                if self.is_running:
                    self.update_admin_password()
                    
            except Exception as e:
                logger.error(f"Ошибка в цикле обновления пароля: {e}")
                time.sleep(60)  # Ждем минуту перед повторной попыткой
    
    def set_custom_credentials(self, username, password):
        """Устанавливает пользовательские учетные данные."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            password_hash = generate_password_hash(password)
            
            if user:
                # Обновляем существующего пользователя
                cursor.execute('''
                    UPDATE users 
                    SET password_hash = ?, role = 'admin'
                    WHERE username = ?
                ''', (password_hash, username))
                action = "обновлен"
            else:
                # Создаем нового пользователя
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role)
                    VALUES (?, ?, 'admin')
                ''', (username, password_hash))
                action = "создан"
            
            conn.commit()
            conn.close()
            
            # Отправляем уведомление через отдельного бота
            success = send_custom_credentials_notification(username, password)
            if success:
                logger.info(f"Пользователь {username} {action} и данные отправлены через отдельного бота")
            else:
                logger.error("Ошибка отправки данных через отдельного бота")
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при установке пользовательских учетных данных: {e}")
            return False
    
    def get_current_password(self, username="admin"):
        """Получает текущий пароль пользователя (только для отладки)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return "Пароль зашифрован в базе данных"
            else:
                return "Пользователь не найден"
                
        except Exception as e:
            logger.error(f"Ошибка при получении пароля: {e}")
            return "Ошибка"

# Глобальный экземпляр менеджера паролей
password_manager = PasswordManager()

def init_password_manager():
    """Инициализация менеджера паролей."""
    global password_manager
    password_manager.start_auto_update()
    logger.info("Менеджер паролей инициализирован")

def cleanup_password_manager():
    """Очистка менеджера паролей."""
    global password_manager
    password_manager.stop_auto_update()
    logger.info("Менеджер паролей остановлен")
