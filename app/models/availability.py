"""Modelo de disponibilidad: qué fechas se pueden reservar y cuántas plazas quedan.

- GROUP_SIZE: plazas por noche (el tamaño del grupo).
- Cada solicitud enviada (pendiente o aceptada) ocupa 1 plaza cada noche de su
  estancia. Las rechazadas no cuentan, así que su plaza vuelve a quedar libre.
- Una noche con todas las plazas ocupadas está "Completo" y no se puede reservar.
- Para cerrar la casa unos días (vacaciones, obras…) añade un rango a BLOCKED_RANGES.
  Cada rango cierra las NOCHES desde `inicio` hasta `fin`, ambos incluidos.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta

GROUP_SIZE = 6  # plazas por noche
BOOKING_WINDOW_DAYS = 365  # hasta cuántos días en el futuro se puede reservar
MIN_NIGHTS = 1
MAX_NIGHTS = 90

# (inicio, fin) en formato AAAA-MM-DD. EJEMPLO: cambia o borra estos rangos.
BLOCKED_RANGES = [
    ("2026-12-22", "2027-01-02"),  # ejemplo: cerrado por Navidad
]

# Datos de EJEMPLO para ver el calendario con plazas ocupadas: (llegada, salida, personas).
# Pon USE_EXAMPLE_DATA = False cuando empieces a recibir solicitudes de verdad.
USE_EXAMPLE_DATA = True
EXAMPLE_STAYS = [
    ("2026-10-20", "2026-10-26", 3),  # este fin de semana: quedan 3
    ("2026-10-26", "2026-11-06", 1),
    ("2026-10-30", "2026-11-08", 2),
    ("2026-11-01", "2026-11-08", 1),  # 1-5 nov: quedan 2
    ("2026-11-09", "2026-11-16", 3),
    ("2026-11-13", "2026-11-16", 3),  # 13-15 nov: completo
    ("2026-11-16", "2026-11-30", 5),  # 16-29 nov: queda 1
    ("2026-12-01", "2026-12-15", 1),
    ("2026-12-05", "2026-12-20", 1),
]


class StayError(ValueError):
    """Fechas no válidas. `code` es la clave del mensaje de error traducido."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class Stay:
    check_in: date
    check_out: date

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days


def _nights(start: date, end: date):
    """Noches de una estancia: desde la llegada hasta el día antes de la salida."""
    day = start
    while day < end:
        yield day
        day += timedelta(days=1)


def _closed_nights() -> set[date]:
    nights = set()
    for start, end in BLOCKED_RANGES:
        nights.update(_nights(date.fromisoformat(start), date.fromisoformat(end) + timedelta(days=1)))
    return nights


def all_booked_stays(application_stays: list[list[str]]) -> list[tuple[str, str, int]]:
    """Estancias que ocupan plaza: las de las solicitudes (1 persona cada una) + las de ejemplo."""
    stays = [(check_in, check_out, 1) for check_in, check_out in application_stays]
    if USE_EXAMPLE_DATA:
        stays += EXAMPLE_STAYS
    return stays


def taken_spots(stays: list[tuple[str, str, int]]) -> Counter:
    """Plazas ocupadas por noche: {date: personas}."""
    taken = Counter()
    for check_in, check_out, people in stays:
        for night in _nights(date.fromisoformat(check_in), date.fromisoformat(check_out)):
            taken[night] += people
    return taken


def _bounds(today: date | None) -> tuple[date, date]:
    first = today or date.today()
    return first, first + timedelta(days=BOOKING_WINDOW_DAYS)


def calendar_config(stays: list[tuple[str, str, int]], today: date | None = None) -> dict:
    """Datos que necesita el calendario del navegador (calendar.js)."""
    first, last = _bounds(today)
    in_window = lambda d: first <= d <= last  # noqa: E731
    return {
        "min": first.isoformat(),
        "max": last.isoformat(),
        "blocked": sorted(d.isoformat() for d in _closed_nights() if in_window(d)),
        "capacity": GROUP_SIZE,
        # Solo las noches con alguien; el resto tiene todas las plazas libres
        "taken": {d.isoformat(): min(n, GROUP_SIZE) for d, n in sorted(taken_spots(stays).items()) if in_window(d)},
        "minNights": MIN_NIGHTS,
        "maxNights": MAX_NIGHTS,
    }


MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"],
}
NIGHTS_LABEL = {"en": ("night", "nights"), "es": ("noche", "noches")}


def format_stay(check_in: str, check_out: str, lang: str) -> str:
    """'2026-11-08', '2026-11-22' -> '8 nov 2026 → 22 nov 2026 · 14 noches'."""
    months = MONTHS.get(lang, MONTHS["en"])
    start, end = date.fromisoformat(check_in), date.fromisoformat(check_out)
    nights = (end - start).days
    one, many = NIGHTS_LABEL.get(lang, NIGHTS_LABEL["en"])

    def fmt(d: date) -> str:
        if lang == "en":
            return f"{months[d.month - 1]} {d.day}, {d.year}"
        return f"{d.day} {months[d.month - 1]} {d.year}"

    return f"{fmt(start)} → {fmt(end)} · {nights} {one if nights == 1 else many}"


def validate_stay(check_in: str, check_out: str, stays: list[tuple[str, str, int]],
                  today: date | None = None) -> Stay:
    """Comprueba en el servidor las fechas elegidas: válidas, abiertas y con plaza."""
    if not check_in or not check_out:
        raise StayError("dates_required")
    try:
        stay = Stay(date.fromisoformat(check_in), date.fromisoformat(check_out))
    except ValueError:
        raise StayError("dates_invalid") from None

    first, last = _bounds(today)
    if stay.check_out <= stay.check_in or stay.check_in < first or stay.check_out > last:
        raise StayError("dates_invalid")
    if not MIN_NIGHTS <= stay.nights <= MAX_NIGHTS:
        raise StayError("dates_length")

    nights = list(_nights(stay.check_in, stay.check_out))
    if any(night in _closed_nights() for night in nights):
        raise StayError("dates_unavailable")
    taken = taken_spots(stays)
    if any(taken[night] >= GROUP_SIZE for night in nights):
        raise StayError("dates_full")
    return stay
