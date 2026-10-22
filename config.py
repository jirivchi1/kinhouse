"""Configuración de la aplicación."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-cambia-esto")
    # Carpeta donde el modelo guarda datos persistentes (suscriptores, etc.)
    DATA_DIR = BASE_DIR / "data"
