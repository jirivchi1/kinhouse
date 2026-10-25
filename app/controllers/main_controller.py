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
    ApplicationRepository,
    InvalidEmailError,
    SubscriberRepository,
    all_booked_stays,
    all_bookings,
    build_form,
    build_member_form,
    calendar_config,
    calendar_events,
    get_home_content,
    get_layout,
    get_ui_text,
)

main_bp = Blueprint("main", __name__)

ONE_YEAR = 60 * 60 * 24 * 365


def render_page(template: str, lang: str, status: int = 200, **context):
    """Renderiza una página en `lang` y recuerda el idioma en una cookie."""
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    response = make_response(render_template(template, layout=get_layout(lang), **context), status)
    response.set_cookie("lang", lang, max_age=ONE_YEAR, samesite="Lax")
    return response


def _applications() -> ApplicationRepository:
    return ApplicationRepository(current_app.config["APPLICATIONS_DIR"])


def booked_stays() -> list:
    """Días de estancia que ocupan plaza: solicitudes enviadas (no rechazadas) + datos de ejemplo."""
    return all_booked_stays(_applications().booked_stays())


def event_bookings():
    """Plazas ocupadas en cada evento: reservas enviadas (no rechazadas) + datos de ejemplo."""
    return all_bookings(_applications().booked_events())


def booking_calendar(lang: str, form) -> dict:
    """Datos del calendario del inicio: plazas de los planes y de los días, y planes de cada día."""
    config = calendar_config(booked_stays())
    return {
        **config,
        "lang": lang,
        "labels": form.texts["calendar"],
        "events": calendar_events(lang, config["min"], config["max"], event_bookings()),
    }


def render_home(lang: str, form=None, member_form=None, status: int = 200,
                open_form: bool = False, open_member: bool = False):
    """Página de inicio. Si un formulario vuelve con errores, se abre ya desplegado."""
    form = form or build_form(lang)
    return render_page(
        "index.html", lang, status=status,
        content=get_home_content(lang),
        form=form,
        member_form=member_form or build_member_form(lang),
        calendar=booking_calendar(lang, form),
        open_form=open_form,
        open_member=open_member,
    )


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
    return render_home(lang)


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
