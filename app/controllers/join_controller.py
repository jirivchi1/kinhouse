"""Controlador de "Únete a la familia".

Las fechas se eligen en el calendario del inicio; al pulsar "Únete a la familia"
se abre el formulario encima de la página y se envía aquí.
"""
from flask import Blueprint, abort, current_app, redirect, request, session, url_for

from app.controllers.main_controller import booked_stays, render_home, render_page
from app.models import (
    SUPPORTED_LANGUAGES,
    ApplicationRepository,
    InvalidEmailError,
    SubscriberRepository,
    build_form,
    format_stay,
    is_spam,
    validate,
)

join_bp = Blueprint("join", __name__)


@join_bp.get("/<lang>/join/")
def form(lang):
    # Ya no hay página propia: el formulario está en el inicio, junto al calendario
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    return redirect(url_for("main.index", lang=lang, _anchor="calendar"))


@join_bp.post("/<lang>/join/")
def submit(lang):
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)

    # A los bots les hacemos creer que ha ido bien, pero no guardamos nada
    if is_spam(request.form):
        return redirect(url_for("join.thanks", lang=lang))

    # Comprueba también que siga habiendo plaza en esas noches
    values, errors = validate(request.form, booked_stays())
    if errors:
        # Vuelve al inicio con el formulario abierto, lo escrito y los errores
        return render_home(lang, build_form(lang, values, errors), status=400, open_form=True)

    ApplicationRepository(current_app.config["APPLICATIONS_DIR"]).save(values, lang)

    if values.get("newsletter"):
        try:
            SubscriberRepository(current_app.config["DATA_DIR"]).add(values["email"])
        except InvalidEmailError:
            pass  # el email ya se validó arriba; no debería pasar

    # Para enseñar las fechas en la página de gracias
    session["last_stay"] = {k: values[k] for k in ("check_in", "check_out", "nights")}

    # Redirigir tras el POST evita que se reenvíe al recargar la página
    return redirect(url_for("join.thanks", lang=lang))


@join_bp.get("/<lang>/join/thanks/")
def thanks(lang):
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    last = session.pop("last_stay", None)
    stay = format_stay(last["check_in"], last["check_out"], lang) if last else None
    return render_page("join_thanks.html", lang, form=build_form(lang), stay=stay)
