"""Configuración de la aplicación."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-cambia-esto")
    # Carpeta donde el modelo guarda datos persistentes (suscriptores, solicitudes…)
    DATA_DIR = BASE_DIR / "data"
    # Una solicitud de "Únete a la familia" = un archivo .json en esta carpeta
    APPLICATIONS_DIR = DATA_DIR / "applications"
