"""Modelo de los eventos que aparecen en el calendario del inicio.

- Viernes, sábado y domingo hay eventos fijos (WEEKLY_PROGRAM), que van
  rotando semana a semana. Las fechas se calculan solas.
- SPECIAL_EVENTS sirve para añadir eventos sueltos en un día concreto.

Para añadir un evento: ponlo en EVENTS y su nombre en TEXTS["en"] y
TEXTS["es"]; luego úsalo en WEEKLY_PROGRAM o en SPECIAL_EVENTS.
"""
from datetime import date, timedelta

from app.models.site_content import DEFAULT_LANGUAGE

# slug: hora
EVENTS = {
    "wine-tasting": "19:00",
    "horse-riding": "10:00",
    "animal-yoga": "11:00",
    "beach-day": "18:30",
    "cows-cheese": "11:00",
    "bbq": "20:00",
}

# Programa de fin de semana que se repite: (viernes, sábado, domingo) de cada semana
WEEKLY_PROGRAM = [
    ("wine-tasting", "horse-riding", "animal-yoga"),
    ("beach-day", "cows-cheese", "bbq"),
]

# Eventos sueltos: {"AAAA-MM-DD": ["slug", ...]}. Ejemplo: {"2026-12-05": ["bbq"]}
SPECIAL_EVENTS: dict[str, list[str]] = {}

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


def calendar_events(lang: str, first: str, last: str) -> dict[str, list[list[str]]]:
    """{"AAAA-MM-DD": [[hora, nombre], ...]} entre `first` y `last` (para calendar.js)."""
    names = TEXTS.get(lang, TEXTS[DEFAULT_LANGUAGE])
    day, end = date.fromisoformat(first), date.fromisoformat(last)
    result = {}
    while day <= end:
        slugs = events_on(day)
        if slugs:
            result[day.isoformat()] = [[EVENTS[slug], names[slug]] for slug in slugs]
        day += timedelta(days=1)
    return result
