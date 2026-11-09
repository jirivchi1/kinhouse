"""Modelo de disponibilidad de las estancias: qué días se pueden reservar y cuántas plazas quedan.

Las estancias se reservan y se cobran POR DÍA: del 8 al 12 son 5 días (ambos
incluidos), y la plaza queda ocupada todos esos días.

- DAILY_CAPACITY: plazas por día en la casa (no es un tamaño de grupo: pueden venir varios grupos).
- Cada solicitud enviada (pendiente o aceptada) ocupa tantas plazas como personas
  apunta cada día de su estancia. Las rechazadas no cuentan: su plaza vuelve a quedar libre.
- Un día con todas las plazas ocupadas está "Completo" y no se puede reservar.
- Para cerrar la casa unos días (vacaciones, obras…) añade un rango a BLOCKED_RANGES.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta

# Pestaña "Unos días" del calendario. Con False solo se pueden reservar planes.
STAYS_ENABLED = True

DAILY_CAPACITY = 6  # plazas por día en la casa (pueden ser de varios grupos de distinto tamaño)
STAY_PRICE_PER_DAY = 20  # € por persona y día (solo se enseña dentro del formulario)
BOOKING_WINDOW_DAYS = 365  # hasta cuántos días en el futuro se puede reservar
MIN_DAYS = 1
MAX_DAYS = 90

# (primer día, último día) cerrados, en formato AAAA-MM-DD. EJEMPLO: cambia o borra estos rangos.
BLOCKED_RANGES = [
    ("2026-12-22", "2027-01-02"),  # ejemplo: cerrado por Navidad
]

# Datos de EJEMPLO para ver el calendario con plazas ocupadas: (primer día, último día, personas).
# Pon USE_EXAMPLE_DATA = False cuando empieces a recibir solicitudes de verdad.
USE_EXAMPLE_DATA = True
EXAMPLE_STAYS = [
    ("2026-10-20", "2026-10-25", 3),  # este fin de semana: quedan 3
    ("2026-10-26", "2026-11-05", 1),
    ("2026-10-30", "2026-11-07", 2),
    ("2026-11-01", "2026-11-07", 1),  # 1-5 nov: quedan 2
    ("2026-11-09", "2026-11-15", 3),
    ("2026-11-13", "2026-11-15", 3),  # 13-15 nov: completo
    ("2026-11-16", "2026-11-29", 5),  # 16-29 nov: queda 1
    ("2026-12-01", "2026-12-14", 1),
    ("2026-12-05", "2026-12-19", 1),
]


class StayError(ValueError):
    """Fechas no válidas. `code` es la clave del mensaje de error traducido."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class Stay:
    check_in: date   # primer día
    check_out: date  # último día (incluido)

    @property
    def days(self) -> int:
        return (self.check_out - self.check_in).days + 1


def _days(start: date, end: date):
    """Todos los días de una estancia, del primero al último (ambos incluidos)."""
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def _closed_days() -> set[date]:
    closed = set()
    for start, end in BLOCKED_RANGES:
        closed.update(_days(date.fromisoformat(start), date.fromisoformat(end)))
    return closed


def all_booked_stays(application_stays: list[list]) -> list[tuple[str, str, int]]:
    """Estancias que ocupan plaza: las de las solicitudes ([primer día, último día, personas]) + las de ejemplo."""
    stays = [(check_in, check_out, people) for check_in, check_out, people in application_stays]
    if USE_EXAMPLE_DATA:
        stays += EXAMPLE_STAYS
    return stays


def taken_spots(stays: list[tuple[str, str, int]]) -> Counter:
    """Plazas ocupadas por día: {date: personas}."""
    taken = Counter()
    for check_in, check_out, people in stays:
        for day in _days(date.fromisoformat(check_in), date.fromisoformat(check_out)):
            taken[day] += people
    return taken


def _bounds(today: date | None) -> tuple[date, date]:
    first = today or date.today()
    return first, first + timedelta(days=BOOKING_WINDOW_DAYS)


def booking_window(today: date | None = None) -> tuple[date, date]:
    """Primer y último día que se pueden reservar (también para los planes)."""
    return _bounds(today)


def calendar_config(stays: list[tuple[str, str, int]], today: date | None = None) -> dict:
    """Datos que necesita el calendario del navegador (calendar.js)."""
    first, last = _bounds(today)
    in_window = lambda d: first <= d <= last  # noqa: E731
    return {
        "min": first.isoformat(),
        "max": last.isoformat(),
        "staysEnabled": STAYS_ENABLED,
        "blocked": sorted(d.isoformat() for d in _closed_days() if in_window(d)),
        "capacity": DAILY_CAPACITY,
        "stayPrice": STAY_PRICE_PER_DAY,
        # Solo los días con alguien; el resto tiene todas las plazas libres
        "taken": {d.isoformat(): min(n, DAILY_CAPACITY) for d, n in sorted(taken_spots(stays).items()) if in_window(d)},
        "minDays": MIN_DAYS,
        "maxDays": MAX_DAYS,
    }


MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"],
}
DAYS_LABEL = {"en": ("day", "days"), "es": ("día", "días")}


def format_stay(check_in: str, check_out: str, lang: str, people=None) -> str:
    """'2026-12-08', '2026-12-12' -> '8 dic 2026 → 12 dic 2026 · 5 días · 2 personas'."""
    months = MONTHS.get(lang, MONTHS["en"])
    start, end = date.fromisoformat(check_in), date.fromisoformat(check_out)
    days = (end - start).days + 1
    one, many = DAYS_LABEL.get(lang, DAYS_LABEL["en"])

    def fmt(d: date) -> str:
        if lang == "en":
            return f"{months[d.month - 1]} {d.day}, {d.year}"
        return f"{d.day} {months[d.month - 1]} {d.year}"

    text = fmt(start) if days == 1 else f"{fmt(start)} → {fmt(end)}"
    text += f" · {days} {one if days == 1 else many}"
    if people:
        n = int(people)
        person = {"en": ("person", "people"), "es": ("persona", "personas")}.get(lang, ("person", "people"))
        text += f" · {n} {person[0] if n == 1 else person[1]}"
    return text


def validate_stay(check_in: str, check_out: str, stays: list[tuple[str, str, int]],
                  people: int = 1, today: date | None = None) -> Stay:
    """Comprueba en el servidor los días elegidos: válidos, abiertos y con plaza."""
    if not check_in or not check_out:
        raise StayError("dates_required")
    try:
        stay = Stay(date.fromisoformat(check_in), date.fromisoformat(check_out))
    except ValueError:
        raise StayError("dates_invalid") from None

    first, last = _bounds(today)
    if stay.check_out < stay.check_in or stay.check_in < first or stay.check_out >= last:
        raise StayError("dates_invalid")
    if not MIN_DAYS <= stay.days <= MAX_DAYS:
        raise StayError("dates_length")

    days = list(_days(stay.check_in, stay.check_out))
    if any(day in _closed_days() for day in days):
        raise StayError("dates_unavailable")
    taken = taken_spots(stays)
    if any(taken[day] + people > DAILY_CAPACITY for day in days):
        raise StayError("dates_full")
    return stay
