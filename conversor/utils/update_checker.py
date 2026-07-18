import re
import json
import urllib.request
import urllib.error
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

from ..utils.logger import logger

GITHUB_API_URL = "https://api.github.com/repos/John54571/Conversor-de-Archivos/releases/latest"
INSTALLER_NAME = "ConversorDeArchivos-Setup.exe"


@dataclass
class ReleaseInfo:
    tag_name: str
    version: str
    body: str
    html_url: str
    installer_url: str
    installer_size: int
    published_at: str


def get_current_version() -> str:
    try:
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent.parent
        
        pyproject_path = base_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding="utf-8")
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
    except Exception as e:
        logger.error(f"Error al leer versión actual: {e}")
    
    return "0.0.0"


def parse_version(version_str: str) -> tuple:
    match = re.search(r'v?(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return (0, 0, 0)


def check_for_updates() -> Optional[ReleaseInfo]:
    try:
        current_version = get_current_version()
        logger.info(f"Versión actual: {current_version}")
        
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        tag_name = data.get("tag_name", "")
        release_version = tag_name.lstrip("v")
        
        current_parsed = parse_version(current_version)
        release_parsed = parse_version(release_version)
        
        if release_parsed <= current_parsed:
            logger.info("La aplicación está actualizada")
            return None
        
        installer_url = None
        installer_size = 0
        
        for asset in data.get("assets", []):
            if asset.get("name", "").endswith(".exe"):
                installer_url = asset.get("browser_download_url", "")
                installer_size = asset.get("size", 0)
                break
        
        if not installer_url:
            logger.warning("No se encontró instalador en el release")
            return None
        
        return ReleaseInfo(
            tag_name=tag_name,
            version=release_version,
            body=data.get("body", ""),
            html_url=data.get("html_url", ""),
            installer_url=installer_url,
            installer_size=installer_size,
            published_at=data.get("published_at", ""),
        )
        
    except urllib.error.HTTPError as e:
        logger.error(f"Error HTTP al verificar actualizaciones: {e.code}")
    except urllib.error.URLError as e:
        logger.error(f"Error de conexión al verificar actualizaciones: {e.reason}")
    except Exception as e:
        logger.error(f"Error al verificar actualizaciones: {e}")
    
    return None


def download_installer(
    installer_url: str,
    download_path: Path,
    on_progress: Optional[Callable[[float, int, int], None]] = None
) -> bool:
    try:
        req = urllib.request.Request(
            installer_url,
            headers={"User-Agent": "ConversorDeArchivos-Updater"}
        )
        
        with urllib.request.urlopen(req, timeout=300) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(download_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if on_progress and total_size > 0:
                        progress = downloaded / total_size
                        on_progress(progress, downloaded, total_size)
        
        logger.info(f"Instalador descargado: {download_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al descargar instalador: {e}")
        if download_path.exists():
            download_path.unlink()
        return False


def run_installer(installer_path: Path) -> bool:
    try:
        if not installer_path.exists():
            logger.error(f"Instalador no encontrado: {installer_path}")
            return False
        
        logger.info(f"Ejecutando instalador: {installer_path}")
        
        subprocess.Popen(
            [str(installer_path)],
            shell=True,
            cwd=str(installer_path.parent)
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error al ejecutar instalador: {e}")
        return False


def get_temp_installer_path() -> Path:
    temp_dir = Path(tempfile.gettempdir()) / "ConversorDeArchivos"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir / INSTALLER_NAME


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
