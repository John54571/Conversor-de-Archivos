import sys
import os
from pathlib import Path
from ..utils.logger import logger


def _get_registry_hive():
    """Obtener el hive de registro apropiado (HKCU no requiere admin)."""
    import winreg
    return winreg.HKEY_CURRENT_USER, r"Software\Classes"


def register_windows_context_menu():
    if sys.platform != "win32":
        logger.warning("Registro de menú contextual solo disponible en Windows")
        return False

    try:
        import winreg
        
        exe_path = sys.executable
        if getattr(sys, "frozen", False):
            exe_path = sys.executable
            logger.debug(f"Modo empaquetado: exe_path={exe_path}")
        else:
            exe_path = f'"{sys.executable}" "{Path(__file__).parent.parent.parent / "main.py"}"'
            logger.debug(f"Modo desarrollo: exe_path={exe_path}")

        menu_text = "Convertir con Conversor de Archivos"
        command = f'{exe_path} "%1"'

        hive, base_path = _get_registry_hive()
        key_path = rf"{base_path}\*\shell\ConversorDeArchivos"
        
        logger.info(f"Registrando menú contextual en HKCU\\{key_path}")
        logger.debug(f"Texto del menú: {menu_text}")
        logger.debug(f"Comando: {command}")
        
        try:
            key = winreg.CreateKey(hive, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_text)
            
            icon_path = exe_path.split('"')[1] if '"' in exe_path else exe_path
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            logger.debug(f"Icono: {icon_path}")
            winreg.CloseKey(key)
            
            command_key = winreg.CreateKey(hive, f"{key_path}\\command")
            winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)
            winreg.CloseKey(command_key)
            
            logger.info("Menú contextual de Windows registrado correctamente en HKCU")
            return True
        except PermissionError as e:
            logger.error(f"Permiso denegado al registrar menú contextual: {e}")
            logger.error("La app necesita permisos de escritura en HKCU\\Software\\Classes")
            return False
        except Exception as e:
            logger.error(f"Error al registrar menú contextual: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
            
    except ImportError:
        logger.error("winreg no disponible")
        return False


def unregister_windows_context_menu():
    if sys.platform != "win32":
        return False

    try:
        import winreg
        
        hive, base_path = _get_registry_hive()
        key_path = rf"{base_path}\*\shell\ConversorDeArchivos"
        
        logger.info(f"Eliminando menú contextual de HKCU\\{key_path}")
        
        try:
            winreg.DeleteKey(hive, f"{key_path}\\command")
            winreg.DeleteKey(hive, key_path)
            logger.info("Menú contextual de Windows eliminado correctamente")
            return True
        except FileNotFoundError:
            logger.warning("Menú contextual no estaba registrado")
            return True
        except PermissionError as e:
            logger.error(f"Permiso denegado al eliminar menú contextual: {e}")
            return False
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
        hive, base_path = _get_registry_hive()
        key_path = rf"{base_path}\*\shell\ConversorDeArchivos"
        
        try:
            key = winreg.OpenKey(hive, key_path)
            
            value, _ = winreg.QueryValueEx(key, "")
            logger.debug(f"Menú contextual encontrado: '{value}'")
            
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            logger.debug("Menú contextual no registrado en HKCU")
            return False
        except Exception as e:
            logger.debug(f"Error al verificar menú contextual: {e}")
            return False
    except ImportError:
        logger.error("winreg no disponible")
        return False


def handle_command_line_args():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        logger.info(f"Argumento de línea de comandos recibido: {file_path}")
        if os.path.exists(file_path):
            logger.info(f"Archivo encontrado: {file_path}")
            return Path(file_path)
        else:
            logger.warning(f"Archivo NO encontrado: {file_path}")
    return None
