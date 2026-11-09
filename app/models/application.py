"""Modelo de las solicitudes de "Únete a la familia".

- FORM_TEXTS: textos de la página y de cada pregunta, en inglés y español.
- SECTIONS: qué preguntas hay, de qué tipo y si son obligatorias.
- validate(): comprueba lo que llega del formulario: la reserva (un evento o
  unos días de estancia) y las respuestas.
- MEMBER_SECTIONS / validate_member(): el formulario para hacerse miembro de la familia.
- ApplicationRepository: guarda cada solicitud como un .json en data/applications/
  (las de miembro llevan "type": "member").

Para añadir o quitar una pregunta: añádela en SECTIONS y pon sus textos en
FORM_TEXTS["en"]["fields"] y FORM_TEXTS["es"]["fields"].
"""
import json
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.models.availability import (
    MAX_DAYS,
    MIN_DAYS,
    STAYS_ENABLED,
    StayError,
    booking_window,
    validate_stay,
)
from app.models.events import MAX_PEOPLE_PER_BOOKING, EventError, validate_event
from app.models.site_content import BRAND, DEFAULT_LANGUAGE, EMAIL

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Campo trampa: invisible para personas, los bots suelen rellenarlo.
HONEYPOT_FIELD = "company_website"


@dataclass
class FieldSpec:
    name: str
    kind: str  # text | email | tel | textarea | radio | select | checkboxes | checkbox
    required: bool = False
    max_length: int = 200
    options: tuple[str, ...] = ()


SECTIONS: list[tuple[str, list[FieldSpec]]] = [
    ("about", [
        # Cuántas personas: sirve igual para un plan que para unos días de estancia
        FieldSpec("people", "select", required=True,
                  options=tuple(str(n) for n in range(1, MAX_PEOPLE_PER_BOOKING + 1))),
        FieldSpec("name", "text", required=True, max_length=100),
        FieldSpec("email", "email", required=True, max_length=200),
        FieldSpec("phone", "tel", max_length=40),
        FieldSpec("project", "textarea", max_length=1000),
    ]),
    ("more", [
        FieldSpec("source", "select",
                  options=("instagram", "youtube", "member", "friend", "search", "other")),
    ]),
    ("consent", [
        FieldSpec("privacy", "checkbox", required=True),
        FieldSpec("newsletter", "checkbox"),
    ]),
]

FIELDS = {spec.name: spec for _, specs in SECTIONS for spec in specs}

# Formulario "Quiero ser miembro": quién eres y qué puedes aportar a la familia
MEMBER_SECTIONS: list[tuple[str, list[FieldSpec]]] = [
    ("member_about", [
        FieldSpec("name", "text", required=True, max_length=100),
        FieldSpec("email", "email", required=True, max_length=200),
        FieldSpec("phone", "tel", max_length=40),
        FieldSpec("profession", "text", required=True, max_length=150),
        FieldSpec("links", "text", max_length=300),
    ]),
    ("member_contribute", [
        FieldSpec("contribution", "checkboxes", required=True,
                  options=("workshop", "mentoring", "plans", "project", "other")),
        FieldSpec("about", "textarea", max_length=1500),
        FieldSpec("source", "select",
                  options=("instagram", "youtube", "member", "friend", "search", "other")),
    ]),
    ("consent", [
        FieldSpec("privacy", "checkbox", required=True),
        FieldSpec("newsletter", "checkbox"),
    ]),
]

MEMBER_FIELDS = {spec.name: spec for _, specs in MEMBER_SECTIONS for spec in specs}


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------
FORM_TEXTS = {
    "en": {
        "title": "Join the family",
        "intro": "Leave us your details to save your spot. It takes less than a minute.",
        "required_note": "Fields marked with * are required.",
        "submit": "Send application",
        "back": "← Back to home",
        "select_placeholder": "Choose an option",
        "error_summary": "Please check the highlighted fields.",
        "errors": {
            "required": "This field is required.",
            "email": "Please enter a valid email.",
            "too_long": "This answer is too long.",
            "invalid_option": "Please choose one of the options.",
            "dates_required": "Choose your check-in and check-out dates.",
            "dates_invalid": "Those dates are not valid. Please choose them again.",
            "dates_length": "Choose between {min} and {max} days.",
            "dates_unavailable": "Some of those days are no longer available. Please choose other dates.",
            "dates_full": "Some of those days just filled up. Please choose other dates.",
            "event_invalid": "That plan is no longer available. Please choose another one in the calendar.",
            "event_full": "That plan just filled up. Please choose another one in the calendar.",
            "event_not_enough": "There aren't enough spots left for that many people. Choose fewer people or another plan.",
        },
        "calendar": {
            "check_in": "Check-in",
            "check_out": "Check-out",
            "add_date": "Add date",
            "clear": "Clear dates",
            "prev": "Previous month",
            "next": "Next month",
            "day": "day",
            "days": "days",
            "pick_check_in": "Select your arrival day",
            "pick_check_out": "Now select your last day (tap the same day if it's just one)",
            "unavailable": "Not available",
            "full": "Full",
            "closed": "Closed",
            "spots_last": "Last spot!",
            "spots_many": "{n} spots",
            "spots_few": "Only {n} left!",
            "spots_legend": "The number on each day is the spots left that day.",
            "events_of": "Events in {month}",
            "no_events": "No events this month yet.",
            "range_empty": "All spots are free on those days: you could be the first!",
            "range_one": "Only 1 spot left on those days!",
            "range_many": "{n} spots left on those days · {taken} people already signed up",
            "your_dates": "Your dates",
            "your_plan": "Your plan",
            "pick_event": "Tap a day with a plan to see it and book your spot",
            "book": "Book a spot",
            "per_person": "per person",
            "left_many": "{n} of {capacity} spots left",
            "left_few": "Only {n} spots left!",
            "left_last": "Last spot!",
            "free_short": "{n} left",
            "events_legend": "Come for the plan and go back home, no need to stay over.",
            "mode_events": "A plan",
            "mode_events_hint": "Wine tasting, horse riding, yoga… you come and go",
            "mode_stays": "A few days",
            "mode_stays_hint": "Stay a few days to work on your idea",
            "per_person_day": "per person and day",
            "price_total": "{amount} in total",
            "pay_later": "You don't pay anything now: we confirm your spot and tell you how to pay.",
            "stay_events_title": "Want to join any plan during your stay?",
            "stay_events_help": "Optional. We'll save your spot in the plan too.",
            "plans": "Plans",
            "people_one": "1 person",
            "people_many": "{n} people",
            "change_dates": "Change dates",
            "change_plan": "Change plan",
            "close": "Close",
        },
        "sections": {
            "about": "About you",
            "more": "One more thing",
            "consent": "Almost done",
            "member_about": "About you",
            "member_contribute": "What you'd bring",
        },
        "fields": {
            "name": {"label": "Full name"},
            "email": {"label": "Email"},
            "people": {"label": "How many of you are coming?",
                       "options": {"1": "Just me", "2": "2 people", "3": "3 people", "4": "4 people"}},
            "phone": {"label": "WhatsApp / phone", "help": "Optional, in case it's easier to talk."},
            "project": {"label": "Do you have an idea or a business?",
                        "help": "Optional. Tell us in a couple of sentences, we love to know who's coming."},
            "source": {"label": "How did you hear about us?", "options": {
                "instagram": "Instagram",
                "youtube": "YouTube",
                "member": "A member of the family",
                "friend": "A friend",
                "search": "Google / search",
                "other": "Other",
            }},
            "privacy": {"label": f"I agree that {BRAND} stores my data to review my application "
                                 f"and contact me about it. You can ask us to delete it at any time "
                                 f"by writing to {EMAIL}."},
            "newsletter": {"label": "I also want to receive the newsletter."},
            "profession": {"label": "What do you do?", "placeholder": "E.g. designer, chef, developer, coach…"},
            "links": {"label": "Instagram, LinkedIn or website", "placeholder": "Where can we see what you do?"},
            "contribution": {"label": "How would you like to contribute?", "options": {
                "workshop": "Running a workshop",
                "mentoring": "Mentoring other members",
                "plans": "Helping with the plans (tastings, routes…)",
                "project": "Sharing my project or business",
                "other": "Something else",
            }},
            "about": {"label": "Tell us a bit more", "help": "Optional. Your idea, what you'd teach, what you're looking for…"},
        },
        "member": {
            "title": "Become a member",
            "intro": "Tell us who you are and what you'd bring to the family. We'll get in touch to meet you.",
            "submit": "Send my request",
            "thanks_title": "Request received!",
            "thanks_text": "Thanks for wanting to be part of the family. We'll write to you in a few days to "
                           "meet you and tell you how the membership works.",
        },
        "thanks_title": "Application received!",
        "thanks_text": "Thanks for applying. Your spot is saved while we review your application. "
                       "We'll send you the info pack by email with everything you need to know: "
                       "the house, the price, activities and next steps.",
        "thanks_dates": "Your dates",
        "thanks_event": "Your plan",
        "thanks_event_text": "Thanks! Your spot is saved. We'll email you the details: how to get "
                             "there, what to bring and how to pay.",
    },
    "es": {
        "title": "Únete a la familia",
        "intro": "Déjanos tus datos para guardar tu plaza. Es menos de un minuto.",
        "required_note": "Los campos con * son obligatorios.",
        "submit": "Enviar solicitud",
        "back": "← Volver al inicio",
        "select_placeholder": "Elige una opción",
        "error_summary": "Revisa los campos marcados.",
        "errors": {
            "required": "Este campo es obligatorio.",
            "email": "Introduce un email válido.",
            "too_long": "Esta respuesta es demasiado larga.",
            "invalid_option": "Elige una de las opciones.",
            "dates_required": "Elige tu fecha de llegada y de salida.",
            "dates_invalid": "Esas fechas no son válidas. Vuelve a elegirlas.",
            "dates_length": "Elige entre {min} y {max} días.",
            "dates_unavailable": "Algunos de esos días ya no están disponibles. Elige otras fechas.",
            "dates_full": "Algunos de esos días se acaban de llenar. Elige otras fechas.",
            "event_invalid": "Ese plan ya no está disponible. Elige otro en el calendario.",
            "event_full": "Ese plan se acaba de llenar. Elige otro en el calendario.",
            "event_not_enough": "No quedan plazas para tantas personas. Elige menos personas u otro plan.",
        },
        "calendar": {
            "check_in": "Llegada",
            "check_out": "Salida",
            "add_date": "Añadir fecha",
            "clear": "Borrar fechas",
            "prev": "Mes anterior",
            "next": "Mes siguiente",
            "day": "día",
            "days": "días",
            "pick_check_in": "Selecciona tu día de llegada",
            "pick_check_out": "Ahora elige tu último día (toca el mismo si es solo uno)",
            "unavailable": "No disponible",
            "full": "Completo",
            "closed": "Cerrado",
            "spots_last": "¡Última plaza!",
            "spots_many": "{n} plazas",
            "spots_few": "¡Quedan {n}!",
            "spots_legend": "El número de cada día son las plazas libres ese día.",
            "events_of": "Eventos de {month}",
            "no_events": "Este mes todavía no hay eventos.",
            "range_empty": "Todas las plazas están libres esos días: ¡puedes ser el primero!",
            "range_one": "¡Solo queda 1 plaza esos días!",
            "range_many": "Quedan {n} plazas esos días · ya hay {taken} personas apuntadas",
            "your_dates": "Tus fechas",
            "your_plan": "Tu plan",
            "pick_event": "Toca un día con plan para verlo y reservar tu plaza",
            "book": "Reservar plaza",
            "per_person": "por persona",
            "left_many": "Quedan {n} de {capacity} plazas",
            "left_few": "¡Solo quedan {n} plazas!",
            "left_last": "¡Última plaza!",
            "free_short": "quedan {n}",
            "events_legend": "Vienes al plan y vuelves a casa: no hace falta quedarse a dormir.",
            "mode_events": "Un plan",
            "mode_events_hint": "Catas, rutas a caballo, yoga… vienes y vuelves",
            "mode_stays": "Unos días",
            "mode_stays_hint": "Quédate unos días a trabajar en tu idea",
            "per_person_day": "por persona y día",
            "price_total": "{amount} en total",
            "pay_later": "No pagas nada ahora: te confirmamos la plaza y te explicamos cómo pagar.",
            "stay_events_title": "¿Te apuntas a algún plan durante tu estancia?",
            "stay_events_help": "Opcional. Te guardamos la plaza también en el plan.",
            "plans": "Planes",
            "people_one": "1 persona",
            "people_many": "{n} personas",
            "change_dates": "Cambiar fechas",
            "change_plan": "Cambiar plan",
            "close": "Cerrar",
        },
        "sections": {
            "about": "Sobre ti",
            "more": "Una última cosa",
            "consent": "Ya casi está",
            "member_about": "Sobre ti",
            "member_contribute": "Lo que aportarías",
        },
        "fields": {
            "name": {"label": "Nombre completo"},
            "email": {"label": "Email"},
            "people": {"label": "¿Cuántas personas venís?",
                       "options": {"1": "Solo yo", "2": "2 personas", "3": "3 personas", "4": "4 personas"}},
            "phone": {"label": "WhatsApp / teléfono", "help": "Opcional, por si es más fácil hablar."},
            "project": {"label": "¿Tienes una idea o un negocio?",
                        "help": "Opcional. Cuéntanoslo en un par de frases, nos encanta saber quién viene."},
            "source": {"label": "¿Cómo nos has conocido?", "options": {
                "instagram": "Instagram",
                "youtube": "YouTube",
                "member": "Un miembro de la familia",
                "friend": "Un amigo o amiga",
                "search": "Google / buscador",
                "other": "Otro",
            }},
            "privacy": {"label": f"Acepto que {BRAND} guarde mis datos para revisar mi solicitud y "
                                 f"contactarme sobre ella. Puedes pedirnos que los borremos cuando "
                                 f"quieras escribiendo a {EMAIL}."},
            "newsletter": {"label": "También quiero recibir la newsletter."},
            "profession": {"label": "¿A qué te dedicas?", "placeholder": "Ej.: diseñadora, cocinero, programador, coach…"},
            "links": {"label": "Instagram, LinkedIn o web", "placeholder": "¿Dónde podemos ver lo que haces?"},
            "contribution": {"label": "¿Cómo te gustaría aportar?", "options": {
                "workshop": "Impartiendo un taller",
                "mentoring": "Como mentor de otros miembros",
                "plans": "Ayudando con los planes (catas, rutas…)",
                "project": "Compartiendo mi proyecto o negocio",
                "other": "Otra cosa",
            }},
            "about": {"label": "Cuéntanos un poco más", "help": "Opcional. Tu idea, qué enseñarías, qué buscas…"},
        },
        "member": {
            "title": "Hazte miembro",
            "intro": "Cuéntanos quién eres y qué aportarías a la familia. Te escribimos para conocerte.",
            "submit": "Enviar mi solicitud",
            "thanks_title": "¡Solicitud recibida!",
            "thanks_text": "Gracias por querer formar parte de la familia. Te escribiremos en unos días para "
                           "conocerte y contarte cómo funciona la membresía.",
        },
        "thanks_title": "¡Solicitud recibida!",
        "thanks_text": "Gracias por apuntarte. Tu plaza queda guardada mientras revisamos tu solicitud. "
                       "Te enviaremos el info pack por email con todo lo que necesitas saber: "
                       "la casa, el precio, las actividades y los siguientes pasos.",
        "thanks_dates": "Tus fechas",
        "thanks_event": "Tu plan",
        "thanks_event_text": "¡Gracias! Tu plaza queda guardada. Te escribiremos por email con los "
                             "detalles: cómo llegar, qué traer y cómo pagar.",
    },
}


# ---------------------------------------------------------------------------
# Estructuras para la vista
# ---------------------------------------------------------------------------
@dataclass
class FormField:
    name: str
    kind: str
    required: bool
    max_length: int
    label: str
    help: str = ""
    placeholder: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)  # (valor, texto)
    value: object = None  # lo que escribió el usuario (para no perderlo si hay errores)
    error: str = ""


@dataclass
class FormSection:
    key: str
    title: str
    fields: list[FormField]


@dataclass
class ApplicationForm:
    texts: dict
    sections: list[FormSection]
    has_errors: bool
    booking_type: str = "event"  # "event" (un plan) o "stay" (unos días)
    event_id: str = ""
    stay_events: list = field(default_factory=list)  # planes elegidos dentro de una estancia
    check_in: str = ""
    check_out: str = ""
    dates_error: str = ""
    id_prefix: str = "f"  # para que los dos formularios de la página no repitan ids
    honeypot: str = HONEYPOT_FIELD


def get_form_texts(lang: str) -> dict:
    return FORM_TEXTS.get(lang, FORM_TEXTS[DEFAULT_LANGUAGE])


def build_form(lang: str, values: dict | None = None, errors: dict | None = None,
               sections_spec: list | None = None, id_prefix: str = "f") -> ApplicationForm:
    """Prepara el formulario para la vista, con los valores y errores si los hay.

    `sections_spec` elige las preguntas: SECTIONS (reservar) por defecto o MEMBER_SECTIONS.
    """
    texts = get_form_texts(lang)
    values = values or {}
    errors = errors or {}

    sections = []
    for key, specs in sections_spec or SECTIONS:
        fields = []
        for spec in specs:
            t = texts["fields"][spec.name]
            labels = t.get("options", {})
            fields.append(FormField(
                name=spec.name,
                kind=spec.kind,
                required=spec.required,
                max_length=spec.max_length,
                label=t["label"],
                help=t.get("help", ""),
                placeholder=t.get("placeholder", ""),
                options=[(opt, labels[opt]) for opt in spec.options],
                value=values.get(spec.name, [] if spec.kind == "checkboxes" else ""),
                error=texts["errors"][errors[spec.name]] if spec.name in errors else "",
            ))
        sections.append(FormSection(key, texts["sections"][key], fields))

    dates_error = ""
    if "dates" in errors:
        dates_error = texts["errors"][errors["dates"]].format(min=MIN_DAYS, max=MAX_DAYS)

    return ApplicationForm(
        texts=texts,
        sections=sections,
        has_errors=bool(errors),
        booking_type=values.get("type", "event"),
        event_id=values.get("event_id", ""),
        stay_events=values.get("stay_events") or [],
        check_in=values.get("check_in", ""),
        check_out=values.get("check_out", ""),
        dates_error=dates_error,
        id_prefix=id_prefix,
    )


def build_member_form(lang: str, values: dict | None = None, errors: dict | None = None) -> ApplicationForm:
    """Formulario "Quiero ser miembro"."""
    return build_form(lang, values, errors, MEMBER_SECTIONS, id_prefix="m")


# ---------------------------------------------------------------------------
# Validación y guardado
# ---------------------------------------------------------------------------
def is_spam(form_data) -> bool:
    return bool((form_data.get(HONEYPOT_FIELD) or "").strip())


def validate(form_data, booked_stays: list, event_bookings: Counter) -> tuple[dict, dict]:
    """Devuelve (valores_limpios, errores). `form_data` es request.form.

    Comprueba también la reserva: un evento con plazas (modo eventos) o unas
    días de estancia con plaza (si la pestaña "Unos días" está activada).
    `booked_stays` y `event_bookings` son lo que ya está ocupado.
    Los errores son claves ("required", "email"…) que build_form() traduce.
    """
    values: dict = {}
    errors: dict = {}

    try:
        people = int(form_data.get("people") or 1)
    except ValueError:
        people = 1
    people = min(max(people, 1), MAX_PEOPLE_PER_BOOKING)

    # Lo que eligió la persona en las pestañas del calendario: un plan o unos días
    if STAYS_ENABLED and form_data.get("booking_type") == "stay":
        values["type"] = "stay"
        values["check_in"] = (form_data.get("check_in") or "").strip()
        values["check_out"] = (form_data.get("check_out") or "").strip()
        values["stay_events"] = list(dict.fromkeys(form_data.getlist("stay_events")))
        try:
            stay = validate_stay(values["check_in"], values["check_out"], booked_stays, people)
            values["days"] = stay.days
            # Planes a los que se apunta durante su estancia (opcional)
            for eid in values["stay_events"]:
                day, _ = validate_event(eid, people, event_bookings, *booking_window())
                if not stay.check_in <= day <= stay.check_out:
                    raise EventError("event_invalid")
        except (StayError, EventError) as exc:
            errors["dates"] = exc.code
    else:
        values["type"] = "event"
        values["event_id"] = (form_data.get("event_id") or "").strip()
        try:
            day, slug = validate_event(values["event_id"], people, event_bookings, *booking_window())
            values["event_date"], values["event"] = day.isoformat(), slug
        except EventError as exc:
            errors["dates"] = exc.code

    _validate_fields(form_data, FIELDS, values, errors)
    return values, errors


def validate_member(form_data) -> tuple[dict, dict]:
    """Solicitud para hacerse miembro: solo las respuestas, no hay fechas ni plazas."""
    values: dict = {"type": "member"}
    errors: dict = {}
    _validate_fields(form_data, MEMBER_FIELDS, values, errors)
    return values, errors


def _validate_fields(form_data, fields: dict, values: dict, errors: dict) -> None:
    """Comprueba cada pregunta y deja lo limpio en `values` y los fallos en `errors`."""
    for name, spec in fields.items():
        if spec.kind == "checkboxes":
            chosen = [v for v in form_data.getlist(name) if v in spec.options]
            values[name] = chosen
            if spec.required and not chosen:
                errors[name] = "required"
            continue

        if spec.kind == "checkbox":
            values[name] = form_data.get(name) == "yes"
            if spec.required and not values[name]:
                errors[name] = "required"
            continue

        value = (form_data.get(name) or "").strip()
        values[name] = value
        if not value:
            if spec.required:
                errors[name] = "required"
        elif len(value) > spec.max_length:
            errors[name] = "too_long"
        elif spec.kind == "email" and not EMAIL_RE.match(value):
            errors[name] = "email"
        elif spec.options and value not in spec.options:
            errors[name] = "invalid_option"

    if values.get("email"):
        values["email"] = values["email"].lower()


class ApplicationRepository:
    """Guarda cada solicitud en su propio archivo JSON."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)

    def save(self, answers: dict, lang: str) -> dict:
        now = datetime.now(timezone.utc)
        application = {
            "id": uuid.uuid4().hex[:12],
            "submitted_at": now.isoformat(timespec="seconds"),
            "lang": lang,
            "status": "pending",  # pending | accepted | rejected (para revisarlas más adelante)
            "info_pack_sent": False,  # cámbialo a true cuando le envíes el info pack
            "answers": answers,
        }
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{now:%Y%m%d-%H%M%S}_{application['id']}.json"
        path.write_text(json.dumps(application, indent=2, ensure_ascii=False), encoding="utf-8")
        return application

    def _active(self) -> list[dict]:
        """Solicitudes que ocupan plaza: pendientes y aceptadas (las "rejected" la dejan libre)."""
        return [a for a in self.all() if a.get("status") != "rejected"]

    @staticmethod
    def _people(answers: dict) -> int:
        try:
            return max(int(answers.get("people") or 1), 1)
        except ValueError:
            return 1

    def booked_stays(self) -> list[list]:
        """[[primer día, último día, personas], ...] de las estancias. Solo fechas, sin datos personales."""
        return [
            [a["answers"]["check_in"], a["answers"]["check_out"], self._people(a["answers"])]
            for a in self._active()
            if a.get("answers", {}).get("check_in")
        ]

    def booked_events(self) -> Counter:
        """Plazas ocupadas por evento: {"AAAA-MM-DD_slug": personas}."""
        taken = Counter()
        for a in self._active():
            answers = a.get("answers", {})
            # El plan reservado suelto y los planes elegidos dentro de una estancia
            for eid in [answers.get("event_id")] + list(answers.get("stay_events") or []):
                if eid:
                    taken[eid] += self._people(answers)
        return taken

    def all(self) -> list[dict]:
        """Todas las solicitudes, de la más reciente a la más antigua."""
        if not self.directory.is_dir():
            return []
        files = sorted(self.directory.glob("*.json"), reverse=True)
        return [json.loads(f.read_text(encoding="utf-8")) for f in files]
