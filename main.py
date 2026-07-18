import sys
import os

if getattr(sys, "frozen", False):
    os.environ["PATH"] = sys._MEIPASS + os.pathsep + os.environ["PATH"]

from conversor.converters.documents import DocumentConverter
from conversor.converters.images import ImageConverter
from conversor.converters.audio import AudioConverter
from conversor.converters.video import VideoConverter
from conversor.ui.app import App
from conversor.utils.logger import logger


def main():
    _ = DocumentConverter
    _ = ImageConverter
    _ = AudioConverter
    _ = VideoConverter

    logger.info("Iniciando Conversor de Archivos")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
