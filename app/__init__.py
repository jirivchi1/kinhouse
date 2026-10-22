"""Fábrica de la aplicación Flask (patrón MVC).

- Modelo:       app/models/       -> datos y reglas de negocio
- Vista:        app/views/        -> plantillas Jinja2 (HTML)
- Controlador:  app/controllers/  -> rutas que conectan modelo y vista
"""
from flask import Flask

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(config_class)

    from app.controllers.main_controller import main_bp

    app.register_blueprint(main_bp)
    return app
