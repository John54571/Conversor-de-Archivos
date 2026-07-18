# Conversor de Archivos

Conversor universal de archivos con interfaz gráfica. Convierte imágenes, audio, video y documentos entre múltiples formatos.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Características

- **Conversión por lotes**: Procesa múltiples archivos simultáneamente
- **Interfaz moderna**: Tema oscuro estilo VLC con drag & drop
- **Vista previa**: Visualiza imágenes, reproduce audio y video
- **Actualizaciones automáticas**: Detecta y descarga nuevas versiones
- **Cola reordenable**: Organiza los archivos antes de convertir
- **Tiempo estimado**: Muestra el tiempo restante de conversión
- **Historial**: Registro de las últimas 1000 conversiones
- **Menú contextual**: Clic derecho → "Convertir con Conversor de Archivos"

## Formatos soportados

### Documentos
| Entrada | Salida |
|---------|--------|
| DOCX, PDF, XLSX, CSV, PPTX, TXT, RTF, HTML, EPUB, ODT | DOCX, PDF, XLSX, CSV, TXT, HTML, EPUB, ODT |

### Imágenes
| Entrada | Salida |
|---------|--------|
| JPG, PNG, BMP, GIF, TIFF, WEBP, ICO, HEIC, SVG | JPG, PNG, BMP, GIF, TIFF, WEBP, ICO, PDF, HEIC |

### Audio
| Entrada | Salida |
|---------|--------|
| MP3, WAV, OGG, FLAC, AAC, WMA, M4A, OPUS, AIFF | MP3, WAV, OGG, FLAC, AAC, WMA, M4A, OPUS, AIFF |

### Video
| Entrada | Salida |
|---------|--------|
| MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V, MPG, MPEG, 3GP, TS | MP4, AVI, MKV, MOV, WEBM, GIF, 3GP |

## Requisitos

- **Sistema operativo**: Windows 10/11 (64-bit)
- **FFmpeg**: Opcional, requerido solo para conversiones de audio y video

## Instalación

1. Descarga el instalador desde la sección [Releases](https://github.com/John54571/Conversor-de-Archivos/releases)
2. Ejecuta `Instalador-ConversorDeArchivos-vX.X.X.exe`
3. Sigue los pasos del asistente de instalación
4. (Opcional) Marca "Instalar FFmpeg" si necesitas conversiones de audio/video

## Uso

1. **Agregar archivos**: Arrastra archivos a la ventana o haz clic en "+ Agregar"
2. **Seleccionar formato**: Elige el formato de destino en el panel central
3. **Configurar calidad**: Ajusta la calidad según tus necesidades
4. **Convertir**: Haz clic en "CONVERTIR" y espera a que termine

### Opciones avanzadas

- **Vista previa**: Selecciona un archivo para ver detalles y reproducir audio/video
- **Reordenar cola**: Usa las flechas ↑↓ para cambiar el orden de conversión
- **Ajustes**: Configura calidad por defecto, reintentos, OCR y más
- **Historial**: Consulta conversiones anteriores con estadísticas

## Desarrollo

### Requisitos

- Python 3.10+
- UV (gestor de paquetes)

### Instalación para desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/John54571/Conversor-de-Archivos.git
cd Conversor-de-Archivos

# Sincronizar dependencias
uv sync

# Ejecutar la aplicación
uv run python main.py
```

### Construir ejecutable

```bash
# Generar .exe
uv run pyinstaller build.spec

# Generar instalador (requiere Inno Setup)
iscc installer/conversor.iss
```

## Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-feature`)
3. Commit tus cambios (`git commit -m 'Agregar nueva feature'`)
4. Push a la rama (`git push origin feature/nueva-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Créditos

Desarrollado por John con Python, CustomTkinter y amor por la conversión de archivos.
