"""Modelo de las solicitudes de "Únete a la familia".

- FORM_TEXTS: textos de la página y de cada pregunta, en inglés y español.
- SECTIONS: qué preguntas hay, de qué tipo y si son obligatorias.
- validate(): comprueba lo que llega del formulario (fechas incluidas).
- ApplicationRepository: guarda cada solicitud como un .json en data/applications/.

Para añadir o quitar una pregunta: añádela en SECTIONS y pon sus textos en
FORM_TEXTS["en"]["fields"] y FORM_TEXTS["es"]["fields"].
"""
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.models.availability import MAX_NIGHTS, MIN_NIGHTS, StayError, validate_stay
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
        FieldSpec("name", "text", required=True, max_length=100),
        FieldSpec("email", "email", required=True, max_length=200),
        FieldSpec("phone", "tel", max_length=40),
        FieldSpec("project", "textarea", required=True, max_length=1000),
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


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------
FORM_TEXTS = {
    "en": {
        "title": "Join the family",
        "intro": "Tell us a bit about you. It takes less than 2 minutes. "
                 "We'll send you the info pack with all the details.",
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
            "dates_length": "Choose between {min} and {max} nights.",
            "dates_unavailable": "Some of those nights are no longer available. Please choose other dates.",
            "dates_full": "Some of those nights just filled up. Please choose other dates.",
        },
        "calendar": {
            "check_in": "Check-in",
            "check_out": "Check-out",
            "add_date": "Add date",
            "clear": "Clear dates",
            "prev": "Previous month",
            "next": "Next month",
            "night": "night",
            "nights": "nights",
            "pick_check_in": "Select your check-in day",
            "pick_check_out": "Now select your check-out day",
            "unavailable": "Not available",
            "full": "Full",
            "closed": "Closed",
            "spots_last": "Last spot!",
            "spots_many": "{n} spots",
            "spots_few": "Only {n} left!",
            "spots_legend": "Groups of {capacity}. The number on each day is the spots left that night.",
            "events_of": "Events in {month}",
            "no_events": "No events this month yet.",
            "range_empty": "All {capacity} spots are free on those dates: you could be the first!",
            "range_one": "Only 1 of {capacity} spots left on those dates!",
            "range_many": "{n} of {capacity} spots left on those dates · {taken} people already signed up",
            "your_dates": "Your dates",
            "change_dates": "Change dates",
            "close": "Close",
        },
        "sections": {
            "about": "About you",
            "more": "One more thing",
            "consent": "Almost done",
        },
        "fields": {
            "name": {"label": "Full name"},
            "email": {"label": "Email"},
            "phone": {"label": "WhatsApp / phone", "help": "Optional, in case it's easier to talk."},
            "project": {"label": "What are you building?", "help": "Tell us in a couple of sentences."},
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
        },
        "thanks_title": "Application received!",
        "thanks_text": "Thanks for applying. Your spot is saved while we review your application. "
                       "We'll send you the info pack by email with everything you need to know: "
                       "the house, the price, activities and next steps.",
        "thanks_dates": "Your dates",
    },
    "es": {
        "title": "Únete a la familia",
        "intro": "Cuéntanos un poco sobre ti. Es menos de 2 minutos. "
                 "Te enviaremos el info pack con todos los detalles.",
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
            "dates_length": "Elige entre {min} y {max} noches.",
            "dates_unavailable": "Algunas de esas noches ya no están disponibles. Elige otras fechas.",
            "dates_full": "Algunas de esas noches se acaban de llenar. Elige otras fechas.",
        },
        "calendar": {
            "check_in": "Llegada",
            "check_out": "Salida",
            "add_date": "Añadir fecha",
            "clear": "Borrar fechas",
            "prev": "Mes anterior",
            "next": "Mes siguiente",
            "night": "noche",
            "nights": "noches",
            "pick_check_in": "Selecciona tu día de llegada",
            "pick_check_out": "Ahora selecciona tu día de salida",
            "unavailable": "No disponible",
            "full": "Completo",
            "closed": "Cerrado",
            "spots_last": "¡Última plaza!",
            "spots_many": "{n} plazas",
            "spots_few": "¡Quedan {n}!",
            "spots_legend": "Grupos de {capacity}. El número de cada día son las plazas libres esa noche.",
            "events_of": "Eventos de {month}",
            "no_events": "Este mes todavía no hay eventos.",
            "range_empty": "Las {capacity} plazas están libres en esas fechas: ¡puedes ser el primero!",
            "range_one": "¡Solo queda 1 de {capacity} plazas en esas fechas!",
            "range_many": "Quedan {n} de {capacity} plazas en esas fechas · ya hay {taken} personas apuntadas",
            "your_dates": "Tus fechas",
            "change_dates": "Cambiar fechas",
            "close": "Cerrar",
        },
        "sections": {
            "about": "Sobre ti",
            "more": "Una última cosa",
            "consent": "Ya casi está",
        },
        "fields": {
            "name": {"label": "Nombre completo"},
            "email": {"label": "Email"},
            "phone": {"label": "WhatsApp / teléfono", "help": "Opcional, por si es más fácil hablar."},
            "project": {"label": "¿Qué estás construyendo?", "help": "Cuéntanoslo en un par de frases."},
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
        },
        "thanks_title": "¡Solicitud recibida!",
        "thanks_text": "Gracias por apuntarte. Tu plaza queda guardada mientras revisamos tu solicitud. "
                       "Te enviaremos el info pack por email con todo lo que necesitas saber: "
                       "la casa, el precio, las actividades y los siguientes pasos.",
        "thanks_dates": "Tus fechas",
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
    check_in: str = ""
    check_out: str = ""
    dates_error: str = ""
    honeypot: str = HONEYPOT_FIELD


def get_form_texts(lang: str) -> dict:
    return FORM_TEXTS.get(lang, FORM_TEXTS[DEFAULT_LANGUAGE])


def build_form(lang: str, values: dict | None = None, errors: dict | None = None) -> ApplicationForm:
    """Prepara el formulario para la vista, con los valores y errores si los hay."""
    texts = get_form_texts(lang)
    values = values or {}
    errors = errors or {}

    sections = []
    for key, specs in SECTIONS:
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
        dates_error = texts["errors"][errors["dates"]].format(min=MIN_NIGHTS, max=MAX_NIGHTS)

    return ApplicationForm(
        texts=texts,
        sections=sections,
        has_errors=bool(errors),
        check_in=values.get("check_in", ""),
        check_out=values.get("check_out", ""),
        dates_error=dates_error,
    )


# ---------------------------------------------------------------------------
# Validación y guardado
# ---------------------------------------------------------------------------
def is_spam(form_data) -> bool:
    return bool((form_data.get(HONEYPOT_FIELD) or "").strip())


def validate(form_data, booked_stays: list) -> tuple[dict, dict]:
    """Devuelve (valores_limpios, errores). `form_data` es request.form.

    `booked_stays` son las estancias que ya ocupan plaza (para no pasar del grupo).
    Los errores son claves ("required", "email"…) que build_form() traduce.
    """
    values: dict = {}
    errors: dict = {}

    values["check_in"] = (form_data.get("check_in") or "").strip()
    values["check_out"] = (form_data.get("check_out") or "").strip()
    try:
        values["nights"] = validate_stay(values["check_in"], values["check_out"], booked_stays).nights
    except StayError as exc:
        errors["dates"] = exc.code

    for name, spec in FIELDS.items():
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
    return values, errors


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

    def booked_stays(self) -> list[list[str]]:
        """[[check_in, check_out], ...] de las solicitudes que ocupan plaza.

        Cuentan las pendientes y las aceptadas; las rechazadas ("rejected") dejan
        su plaza libre. Solo fechas, sin datos personales.
        """
        return [
            [a["answers"]["check_in"], a["answers"]["check_out"]]
            for a in self.all()
            if a.get("status") != "rejected" and a.get("answers", {}).get("check_in")
        ]

    def all(self) -> list[dict]:
        """Todas las solicitudes, de la más reciente a la más antigua."""
        if not self.directory.is_dir():
            return []
        files = sorted(self.directory.glob("*.json"), reverse=True)
        return [json.loads(f.read_text(encoding="utf-8")) for f in files]
