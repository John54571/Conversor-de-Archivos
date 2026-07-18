# AGENTS.md - Conversor de Archivos

## Descripcion general

Conversor universal de archivos con GUI en Python. Soporta conversiones entre formatos de imagenes, audio, video y documentos. Interfaz estilo Excel/Unity con CustomTkinter.

## Estructura del proyecto

```
Conversor de Archivos/
├── main.py                 # Entry point principal
├── pyproject.toml          # Configuracion UV + dependencias
├── uv.lock                 # Lock file (NO editar manualmente)
├── .venv/                  # Entorno virtual (ignorar en git)
├── AGENTS.md               # Este archivo
├── build.spec              # Configuracion PyInstaller para .exe
└── conversor/
    ├── __init__.py
    ├── core/               # Logica de negocio
    │   ├── engine.py       # Motor de conversion con ThreadPoolExecutor
    │   ├── registry.py     # Registro de convertidores (pattern Registry)
    │   └── validators.py   # Validacion de conversiones y helpers
    ├── converters/         # Implementaciones de conversion
    │   ├── base.py         # BaseConverter (clase abstracta), ConversionTask, enums
    │   ├── documents.py    # DOCX, PDF, XLSX, CSV, PPTX, TXT, RTF, HTML
    │   ├── images.py       # JPG, PNG, WEBP, BMP, GIF, TIFF, ICO
    │   ├── audio.py        # MP3, WAV, OGG, FLAC, AAC, WMA, M4A, OPUS
    │   └── video.py        # MP4, AVI, MKV, MOV, WEBM, GIF
    ├── ui/                 # Interfaz grafica (CustomTkinter)
    │   ├── app.py          # Ventana principal
    │   ├── file_panel.py   # Panel izquierdo: lista de archivos
    │   ├── options_panel.py # Panel central: formato destino + calidad
    │   ├── progress_panel.py # Panel derecho: progreso individual
    │   └── themes.py       # Paleta de colores, fuentes, tamanos
    └── utils/              # Utilidades
        ├── ffmpeg_check.py # Deteccion de FFmpeg en el sistema
        └── file_utils.py   # Helpers (info de archivos, iconos, filtros)
```

## Comandos esenciales (UV)

```bash
# Ejecutar el programa
uv run python main.py

# Agregar nueva dependencia
uv add <paquete>

# Remover dependencia
uv remove <paquete>

# Sincronizar entorno (instalar/actualizar desde pyproject.toml)
uv sync

# Actualizar todas las dependencias
uv sync --upgrade

# Activar entorno virtual manualmente (opcional, uv run ya lo activa)
.venv\Scripts\activate

# Construir ejecutable .exe
uv run pyinstaller build.spec

# Ver dependencias instaladas
uv pip list

# Ver arbol de dependencias
uv pip tree
```

## Convenciones de codigo

### Python
- **Version minima**: Python 3.10
- **Type hints**: Usar sintaxis moderna (`list[str]` en vez de `List[str]`, `dict[str, int]` en vez de `Dict[str, int]`)
- **Imports**: Absolutos desde `conversor.*` (ej: `from conversor.core.registry import ConverterRegistry`)
- **Encoding**: Siempre `encoding="utf-8"` al leer/escribir archivos de texto
- **Path**: Usar `pathlib.Path` en vez de `os.path`

### Arquitectura
- **Registry pattern**: Los convertidores se registran con `@ConverterRegistry.register`
- **BaseConverter**: Clase abstracta que todos los convertidores deben extender
- **ConversionTask**: Dataclass que representa una tarea de conversion individual
- **ConversionEngine**: ThreadPoolExecutor para concurrencia (max 3 workers por defecto)
- **GUI**: CustomTkinter con tema claro, colores corporativos (azul #2B579A)

### Estilo visual
- **Fondo**: Gris claro (#F0F0F0)
- **Header/Acento**: Azul corporativo (#2B579A)
- **Fuente**: Segoe UI (nativa de Windows)
- **Layout**: 3 paneles (archivos | opciones | progreso)
- **Inspiracion**: UserForms de Excel / Unity Real Time

## Como agregar un nuevo convertidor

```python
# conversor/converters/nuevo_converter.py

from pathlib import Path
from .base import BaseConverter, ConversionTask, FileCategory
from ..core.registry import ConverterRegistry


@ConverterRegistry.register
class NuevoConverter(BaseConverter):
    SUPPORTED_INPUT = ["ext1", "ext2"]      # Extensiones que puede leer
    SUPPORTED_OUTPUT = ["ext3", "ext4"]     # Extensiones que puede generar
    CATEGORY = FileCategory.DOCUMENT        # O AUDIO, IMAGE, VIDEO

    def convert(self, task: ConversionTask) -> Path:
        src = task.source_path
        tgt_ext = task.output_format
        output_dir = Path(task.options.output_dir or src.parent)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{src.stem}.{tgt_ext}"

        # Implementar la conversion aqui
        # ...

        if task.on_progress:
            task.on_progress(0.5)  # Reportar progreso (0.0 a 1.0)

        # Guardar resultado en output_path
        # ...

        if task.on_progress:
            task.on_progress(1.0)

        return output_path
```

Luego importar en `main.py`:
```python
from conversor.converters.nuevo_converter import NuevoConverter
```

## Dependencias principales

| Paquete | Uso |
|---------|-----|
| `customtkinter` | GUI (ventanas, botones, paneles) |
| `Pillow` | Conversion de imagenes |
| `pydub` | Conversion de audio (requiere FFmpeg) |
| `ffmpeg-python` | Conversion de video (requiere FFmpeg) |
| `python-docx` | Leer/escribir archivos Word |
| `pypdf` | Leer archivos PDF |
| `pdf2docx` | Convertir PDF a DOCX |
| `openpyxl` | Leer/escribir archivos Excel |
| `pandas` | Manipular datos CSV/Excel |
| `python-pptx` | Leer archivos PowerPoint |
| `fpdf2` | Generar archivos PDF |
| `pdf2image` | Convertir paginas PDF a imagenes |
| `pyinstaller` | Generar ejecutable .exe |

## Dependencia externa: FFmpeg

**Requerido para**: Audio y Video

El programa detecta automaticamente si FFmpeg esta instalado. Si no lo esta, las conversiones de audio/video no funcionaran pero las de imagenes/documentos si.

**Instalacion en Windows**:
1. Descargar desde https://ffmpeg.org/download.html
2. Extraer el ZIP
3. Agregar la carpeta `bin/` al PATH del sistema
4. Reiniciar terminal

**Verificar instalacion**:
```bash
ffmpeg -version
```

## Conversiones soportadas

### Documentos
- **Entrada**: DOCX, PDF, XLSX, CSV, PPTX, TXT, RTF, HTML
- **Salida**: DOCX, PDF, XLSX, CSV, TXT, HTML
- **Nota**: Algunas combinaciones no son posibles (ej: XLSX -> DOCX)

### Imagenes
- **Entrada**: JPG, PNG, BMP, GIF, TIFF, WEBP, ICO
- **Salida**: JPG, PNG, BMP, GIF, TIFF, WEBP, ICO, PDF
- **Calidad**: Baja (50%), Media (75%), Alta (90%), Maxima (100%)

### Audio
- **Entrada**: MP3, WAV, OGG, FLAC, AAC, WMA, M4A, OPUS
- **Salida**: MP3, WAV, OGG, FLAC, AAC, WMA, M4A, OPUS
- **Calidad**: 64, 96, 128, 192, 256, 320 kbps

### Video
- **Entrada**: MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V, MPG, MPEG
- **Salida**: MP4, AVI, MKV, MOV, WEBM, GIF
- **Resolucion**: 480p, 720p, 1080p, 2160p (4K)

## Notas importantes

- **Batch**: Soporta multiples archivos simultaneos (cola con 3 workers)
- **Progreso**: Individual por archivo + progreso global
- **Cancelacion**: Se pueden cancelar tareas pendientes
- **Portabilidad**: El `uv.lock` garantiza instalaciones reproducibles
- **Empaquetado**: `build.spec` configurado para PyInstaller (genera un solo .exe)

## Testing

No hay tests automatizados aun. Para verificar manualmente:

```bash
# Verificar imports
uv run python -c "from conversor.converters.documents import DocumentConverter; print('OK')"

# Ejecutar pruebas de conversion (crear archivos de prueba primero)
uv run python -c "
from pathlib import Path
from conversor.converters.images import ImageConverter
from conversor.converters.base import ConversionTask, ConversionOptions, FileCategory
from PIL import Image

# Crear imagen de prueba
img = Image.new('RGB', (100, 100), color='red')
src = Path('test.png')
img.save(str(src))

# Convertir
task = ConversionTask(
    id='test', source_path=src, output_format='jpg',
    category=FileCategory.IMAGE,
    options=ConversionOptions(output_format='jpg')
)
result = ImageConverter().convert(task)
print(f'Convertido: {result} (existe: {result.exists()})')
"
```

## Troubleshooting

### Error: "FFmpeg no encontrado"
- FFmpeg no esta en el PATH
- Solucion: Instalar FFmpeg y agregarlo al PATH

### Error: "No module named 'conversor'"
- El entorno virtual no esta activado
- Solucion: Usar `uv run python main.py` en vez de `python main.py`

### Error: "hatchling build failed"
- Falta configurar `tool.hatch.build.targets.wheel` en `pyproject.toml`
- Solucion: Verificar que exista `packages = ["conversor"]`

### La GUI no abre
- Verificar que CustomTkinter esta instalado: `uv pip list | grep customtkinter`
- En Windows, puede haber conflictos con DPI scaling
- Solucion: Ejecutar desde terminal con `uv run python main.py`
