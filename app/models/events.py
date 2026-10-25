"""Modelo de los eventos (planes de tarde) que se reservan desde el calendario del inicio.

- Viernes, sábado y domingo hay eventos fijos (WEEKLY_PROGRAM), que van
  rotando semana a semana. Las fechas se calculan solas.
- SPECIAL_EVENTS sirve para añadir eventos sueltos en un día concreto.
- Cada evento tiene hora, precio por persona y plazas. Cada reserva (pendiente
  o aceptada) ocupa tantas plazas como personas apunta.

Para añadir un evento: ponlo en EVENTS y su nombre en TEXTS["en"] y
TEXTS["es"]; luego úsalo en WEEKLY_PROGRAM o en SPECIAL_EVENTS.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta

from app.models.availability import MONTHS
from app.models.site_content import DEFAULT_LANGUAGE

MAX_PEOPLE_PER_BOOKING = 4  # cuántas personas se pueden apuntar en una misma reserva


@dataclass(frozen=True)
class EventType:
    time: str
    price: int  # € por persona
    capacity: int  # plazas


EVENTS = {
    "wine-tasting": EventType("19:00", 25, 12),
    "horse-riding": EventType("10:00", 35, 6),
    "animal-yoga": EventType("11:00", 15, 10),
    "beach-day": EventType("18:30", 10, 15),
    "cows-cheese": EventType("11:00", 20, 12),
    "bbq": EventType("20:00", 25, 20),
}

# Programa de fin de semana que se repite: (viernes, sábado, domingo) de cada semana
WEEKLY_PROGRAM = [
    ("wine-tasting", "horse-riding", "animal-yoga"),
    ("beach-day", "cows-cheese", "bbq"),
]

# Eventos sueltos: {"AAAA-MM-DD": ["slug", ...]}. Ejemplo: {"2026-12-05": ["bbq"]}
SPECIAL_EVENTS: dict[str, list[str]] = {}

# Reservas de EJEMPLO para ver el calendario con plazas ocupadas: {"AAAA-MM-DD_slug": personas}.
# Pon USE_EXAMPLE_DATA = False cuando empieces a recibir reservas de verdad.
USE_EXAMPLE_DATA = True
EXAMPLE_BOOKINGS = {
    "2026-10-30_wine-tasting": 9,   # quedan 3
    "2026-10-31_horse-riding": 6,   # completo
    "2026-11-01_animal-yoga": 4,
    "2026-11-06_beach-day": 5,
    "2026-11-07_cows-cheese": 11,   # queda 1
    "2026-11-08_bbq": 8,
}

TEXTS = {
    "en": {
        "wine-tasting": "Wine tasting",
        "horse-riding": "Horse riding",
        "animal-yoga": "Yoga with animals",
        "beach-day": "Beach outing",
        "cows-cheese": "Cows & cheese visit",
        "bbq": "Barbecue & campfire",
    },
    "es": {
        "wine-tasting": "Cata de vinos",
        "horse-riding": "Ruta a caballo",
        "animal-yoga": "Yoga con animales",
        "beach-day": "Salida a la playa",
        "cows-cheese": "Vacas y quesos",
        "bbq": "Barbacoa y hoguera",
    },
}


class EventError(ValueError):
    """Reserva de evento no válida. `code` es la clave del mensaje de error traducido."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def events_on(day: date) -> list[str]:
    """Slugs de los eventos de un día."""
    slugs = []
    if day.weekday() >= 4:  # viernes, sábado, domingo
        monday = day - timedelta(days=day.weekday())
        # La semana del año decide qué programa toca, así no cambia al recargar
        program = WEEKLY_PROGRAM[monday.isocalendar().week % len(WEEKLY_PROGRAM)]
        slugs.append(program[day.weekday() - 4])
    slugs.extend(SPECIAL_EVENTS.get(day.isoformat(), []))
    return slugs


def event_id(day: date, slug: str) -> str:
    """Identificador de un evento concreto: '2026-10-30_wine-tasting'."""
    return f"{day.isoformat()}_{slug}"


def all_bookings(application_bookings: Counter) -> Counter:
    """Plazas ocupadas por evento: reservas de las solicitudes + las de ejemplo."""
    taken = Counter(application_bookings)
    if USE_EXAMPLE_DATA:
        taken.update(EXAMPLE_BOOKINGS)
    return taken


def event_name(slug: str, lang: str) -> str:
    return TEXTS.get(lang, TEXTS[DEFAULT_LANGUAGE])[slug]


def calendar_events(lang: str, first: str, last: str, taken: Counter) -> dict[str, list[dict]]:
    """{"AAAA-MM-DD": [{id, time, name, price, capacity, free}, ...]} entre `first` y `last`."""
    day, end = date.fromisoformat(first), date.fromisoformat(last)
    result = {}
    while day <= end:
        items = []
        for slug in events_on(day):
            event = EVENTS[slug]
            eid = event_id(day, slug)
            items.append({
                "id": eid,
                "time": event.time,
                "name": event_name(slug, lang),
                "price": event.price,
                "capacity": event.capacity,
                "free": max(event.capacity - taken[eid], 0),
            })
        if items:
            result[day.isoformat()] = items
        day += timedelta(days=1)
    return result


def validate_event(eid: str, people: int, taken: Counter, first: date, last: date) -> tuple[date, str]:
    """Comprueba en el servidor la reserva de un evento: que exista, sea futuro y tenga plazas."""
    try:
        day_text, slug = eid.split("_", 1)
        day = date.fromisoformat(day_text)
    except ValueError:
        raise EventError("event_invalid") from None
    if not first <= day <= last or slug not in events_on(day):
        raise EventError("event_invalid")
    capacity = EVENTS[slug].capacity
    if taken[eid] >= capacity:
        raise EventError("event_full")
    if taken[eid] + people > capacity:
        raise EventError("event_not_enough")
    return day, slug


WEEKDAYS = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "es": ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"],
}
PEOPLE_LABEL = {"en": ("person", "people"), "es": ("persona", "personas")}


def format_event_booking(slug: str, day: str, people, lang: str) -> str:
    """'Cata de vinos · vie 30 oct 2026 · 19:00 · 2 personas'."""
    d = date.fromisoformat(day)
    months = MONTHS.get(lang, MONTHS["en"])
    weekday = WEEKDAYS.get(lang, WEEKDAYS["en"])[d.weekday()]
    when = f"{weekday} {months[d.month - 1]} {d.day}, {d.year}" if lang == "en" \
        else f"{weekday} {d.day} {months[d.month - 1]} {d.year}"
    n = int(people or 1)
    one, many = PEOPLE_LABEL.get(lang, PEOPLE_LABEL["en"])
    return f"{event_name(slug, lang)} · {when} · {EVENTS[slug].time} · {n} {one if n == 1 else many}"


def format_event_short(eid: str, lang: str) -> str:
    """'2026-10-30_wine-tasting' -> 'Cata de vinos (vie 30 oct, 19:00)'."""
    day_text, slug = eid.split("_", 1)
    d = date.fromisoformat(day_text)
    month = MONTHS.get(lang, MONTHS["en"])[d.month - 1]
    weekday = WEEKDAYS.get(lang, WEEKDAYS["en"])[d.weekday()]
    when = f"{weekday} {month} {d.day}" if lang == "en" else f"{weekday} {d.day} {month}"
    return f"{event_name(slug, lang)} ({when}, {EVENTS[slug].time})"
