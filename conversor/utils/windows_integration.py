import sys
import os
from pathlib import Path
from ..utils.logger import logger


def register_windows_context_menu():
    if sys.platform != "win32":
        logger.warning("Registro de menú contextual solo disponible en Windows")
        return False

    try:
        import winreg
        
        exe_path = sys.executable
        if getattr(sys, "frozen", False):
            exe_path = sys.executable
        else:
            exe_path = f'"{sys.executable}" "{Path(__file__).parent.parent.parent / "main.py"}"'

        menu_text = "Convertir con Conversor de Archivos"
        command = f'{exe_path} "%1"'

        key_path = r"*\shell\ConversorDeArchivos"
        
        try:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_text)
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path.split('"')[1] if '"' in exe_path else exe_path)
            winreg.CloseKey(key)
            
            command_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command")
            winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)
            winreg.CloseKey(command_key)
            
            logger.info("Menú contextual de Windows registrado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al registrar menú contextual: {e}")
            return False
            
    except ImportError:
        logger.error("winreg no disponible")
        return False


def unregister_windows_context_menu():
    if sys.platform != "win32":
        return False

    try:
        import winreg
        
        key_path = r"*\shell\ConversorDeArchivos"
        
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
            logger.info("Menú contextual de Windows eliminado correctamente")
            return True
        except FileNotFoundError:
            logger.warning("Menú contextual no estaba registrado")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar menú contextual: {e}")
            return False
            
    except ImportError:
        logger.error("winreg no disponible")
        return False


def is_context_menu_registered() -> bool:
    if sys.platform != "win32":
        return False

    try:
        import winreg
        key_path = r"*\shell\ConversorDeArchivos"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
    except Exception:
        return False


def handle_command_line_args():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            return Path(file_path)
    return None
