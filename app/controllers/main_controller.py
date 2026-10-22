"""Controlador principal: une el modelo con las vistas."""
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    InvalidEmailError,
    SubscriberRepository,
    get_home_content,
    get_ui_text,
)

main_bp = Blueprint("main", __name__)

ONE_YEAR = 60 * 60 * 24 * 365


@main_bp.get("/")
def root():
    """Redirige al idioma guardado o, si no hay, al del navegador."""
    lang = request.cookies.get("lang")
    if lang not in SUPPORTED_LANGUAGES:
        lang = request.accept_languages.best_match(SUPPORTED_LANGUAGES) or DEFAULT_LANGUAGE
    return redirect(url_for("main.index", lang=lang))


@main_bp.get("/<lang>/")
def index(lang):
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    response = make_response(render_template("index.html", content=get_home_content(lang)))
    response.set_cookie("lang", lang, max_age=ONE_YEAR, samesite="Lax")
    return response


@main_bp.post("/subscribe")
def subscribe():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    lang = data.get("lang", DEFAULT_LANGUAGE)
    repo = SubscriberRepository(current_app.config["DATA_DIR"])
    try:
        created = repo.add(data.get("email"))
    except InvalidEmailError:
        return jsonify(ok=False, message=get_ui_text(lang, "invalid_email")), 400

    message = get_ui_text(lang, "subscribed" if created else "already_subscribed")
    return jsonify(ok=True, message=message)
