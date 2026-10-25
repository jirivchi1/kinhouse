"""Controlador de las solicitudes: reservar (plan o días) y hacerse miembro.

Las fechas se eligen en el calendario del inicio; al pulsar "Únete a la familia"
se abre el formulario encima de la página y se envía aquí.
"""
from flask import Blueprint, abort, current_app, redirect, request, session, url_for

from app.controllers.main_controller import booked_stays, event_bookings, render_home, render_page
from app.models import (
    SUPPORTED_LANGUAGES,
    ApplicationRepository,
    InvalidEmailError,
    SubscriberRepository,
    build_form,
    build_member_form,
    format_event_booking,
    format_event_short,
    format_stay,
    is_spam,
    validate,
    validate_member,
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

    # Comprueba también que siga habiendo plaza (en el plan o en esos días)
    values, errors = validate(request.form, booked_stays(), event_bookings())
    if errors:
        # Vuelve al inicio con el formulario abierto, lo escrito y los errores
        return render_home(lang, build_form(lang, values, errors), status=400, open_form=True)

    ApplicationRepository(current_app.config["APPLICATIONS_DIR"]).save(values, lang)

    if values.get("newsletter"):
        try:
            SubscriberRepository(current_app.config["DATA_DIR"]).add(values["email"])
        except InvalidEmailError:
            pass  # el email ya se validó arriba; no debería pasar

    # Para enseñar lo reservado en la página de gracias
    session["last_booking"] = {k: values.get(k) for k in ("type", "check_in", "check_out", "event_date", "event", "people", "stay_events")}

    # Redirigir tras el POST evita que se reenvíe al recargar la página
    return redirect(url_for("join.thanks", lang=lang))


@join_bp.get("/<lang>/join/thanks/")
def thanks(lang):
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    last = session.pop("last_booking", None)
    summary, plans = None, []
    if last and last.get("type") == "stay":
        summary = format_stay(last["check_in"], last["check_out"], lang, last["people"])
        plans = [format_event_short(eid, lang) for eid in last.get("stay_events") or []]
    elif last and last.get("type") == "event":
        summary = format_event_booking(last["event"], last["event_date"], last["people"], lang)
    texts = build_form(lang).texts
    is_event = bool(last and last.get("type") == "event")
    return render_page(
        "join_thanks.html", lang, form=build_form(lang), summary=summary, plans=plans, is_event=is_event,
        title=texts["thanks_title"],
        text=texts["thanks_event_text"] if is_event else texts["thanks_text"],
    )


@join_bp.post("/<lang>/member/")
def member_submit(lang):
    """Solicitud "Quiero ser miembro" (formulario de la sección de la familia)."""
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    if is_spam(request.form):
        return redirect(url_for("join.member_thanks", lang=lang))

    values, errors = validate_member(request.form)
    if errors:
        return render_home(lang, member_form=build_member_form(lang, values, errors), status=400, open_member=True)

    ApplicationRepository(current_app.config["APPLICATIONS_DIR"]).save(values, lang)
    if values.get("newsletter"):
        try:
            SubscriberRepository(current_app.config["DATA_DIR"]).add(values["email"])
        except InvalidEmailError:
            pass
    return redirect(url_for("join.member_thanks", lang=lang))


@join_bp.get("/<lang>/member/thanks/")
def member_thanks(lang):
    if lang not in SUPPORTED_LANGUAGES:
        abort(404)
    texts = build_form(lang).texts["member"]
    return render_page("join_thanks.html", lang, form=build_form(lang), summary=None, plans=[], is_event=False,
                       title=texts["thanks_title"], text=texts["thanks_text"])
