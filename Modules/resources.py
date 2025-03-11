import os
import sys

class ResourceManager:
    """Clase para manejar los recursos del programa, como imágenes, asegurando compatibilidad con PyInstaller."""
    
    @staticmethod
    def get_path(relative_path):
        """Devuelve la ruta absoluta del recurso, compatible con ejecución normal y PyInstaller."""
        try:
            base_path = sys._MEIPASS  # Cuando se ejecuta desde un .exe empaquetado con PyInstaller
        except AttributeError:
            base_path = os.path.abspath("source")  # En desarrollo, la carpeta donde están los recursos

        return os.path.join(base_path, relative_path)

# Ruta del ícono del programa
ICON_PATH = ResourceManager.get_path("panda.png")
