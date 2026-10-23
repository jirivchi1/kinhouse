"""Modelo de contenido de la página.

Todo el texto e imágenes de la web viven aquí: para cambiar la página
solo tienes que editar este archivo (o sustituirlo por una base de datos).

- Lo que no depende del idioma (fotos, nombres, enlaces) está en las
  constantes de arriba.
- Los textos traducidos están en TEXTS["en"] y TEXTS["es"], en el mismo
  orden que las fotos/personas a las que acompañan.
"""
from dataclasses import dataclass
from pathlib import Path

from app.models.availability import GROUP_SIZE

SUPPORTED_LANGUAGES = ("en", "es")
DEFAULT_LANGUAGE = "en"

BRAND = "Kinhaus"
EMAIL = "hi@kinhaus.co"
SOCIAL_URLS = ["https://www.instagram.com/", "https://www.youtube.com/"]

IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def unsplash(photo_id: str, width: int = 800, height: int | None = None) -> str:
    """URL de una imagen de Unsplash recortada al tamaño pedido."""
    url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={width}&q=80"
    if height:
        url += f"&h={height}"
    return url


def local_image(folder: str, name: str, fallback: str) -> str:
    """Foto propia de app/static/img/<folder>/<name>.<jpg|jpeg|png|webp|avif>.

    Si no existe, devuelve `fallback` (la foto de Unsplash). No importa la
    extensión ni las mayúsculas. El ?v= hace que el navegador recargue la
    foto cuando la sustituyes por otra con el mismo nombre.
    """
    directory = IMG_DIR / folder
    if directory.is_dir():
        for file in directory.iterdir():
            if file.stem.lower() == name.lower() and file.suffix.lower() in IMAGE_EXTENSIONS:
                return f"/static/img/{folder}/{file.name}?v={int(file.stat().st_mtime)}"
    return fallback


# ---------------------------------------------------------------------------
# Datos que no cambian con el idioma
# ---------------------------------------------------------------------------
HERO_PHOTO = ("portada", "portada", "1600596542815-ffad4c1539a9")  # (carpeta, nombre, reserva)
HERO_VIDEO = None  # p. ej. "/static/video/hero.mp4"

EXPERIENCE_PHOTOS = [
    "1612872087720-bb876e2e67d1",
    "1523240795612-9a054b0db644",
    "1530541930197-ff16ac917b0e",
    "1506126613408-eca07ce68773",
    "1543269865-cbf427effbad",
    "1511632765486-a01980e01a18",
    "1501555088652-021faa106b9b",
    "1517457373958-b7bdd4587205",
    "1475483768296-6163e08872a1",
    "1522202176988-66273c2fd55f",
]

# Pestañas de "Cómo trabajamos": (slug, foto propia en img/como-nos-movemos/, foto de reserva)
OFFERINGS = [
    ("founder-houses", "casas_fundadores", "1613490493576-7fde63acd811"),
    ("weekly-calls", "llamadas_semanales", "1588196749597-9ff075ee6b5b"),
    ("online-platform", "plataforma_online", "1531545514256-b1400bc00f31"),
    ("workshops", "talleres", "1552664730-d307ca884978"),
    ("mentorship", "mentoria", "1544027993-37dbfe43562a"),
]

PEOPLE = [  # (nombre, país, avatar)
    ("Lara", "NL", "1494790108377-be9c29b29330"),
    ("Joris", "NL", "1507003211169-0a1dd7228f2d"),
    ("Michelle", "ZA", "1438761681033-6461ffad8d80"),
    ("Patrick", "AU", "1500648767791-00dcc994a43e"),
    ("Matthieu", "NL", "1472099645785-5658abf4ff4e"),
]


# ---------------------------------------------------------------------------
# Textos traducidos
# ---------------------------------------------------------------------------
TEXTS = {
    "en": {
        "language_name": "English",
        "meta_description": "A private community for early-stage lifestyle founders.",
        "hero_headline": ["Unplug from the routine,", "reconnect with what matters."],
        "scroll_hint": "↓ scroll to learn more",
        "intro_title": "Clear your head for a weekend, break the routine or move your idea forward: "
                       "a country house and people who help you do it.",
        "intro_paragraphs": [
            [
                "We believe growth doesn't happen in isolation.",
                "It happens in the right environment, with the right people, who want the same out of life.",
            ],
            [
                "That's why we exist.",
                "So you can break through your barriers and start living the life you always envisioned.",
            ],
        ],
        "quote": [
            "You become like the five people you spend the",
            "most time with. Choose carefully.  - Jim Rohn",
        ],
        "join": "Join the family",
        "experiences": [  # (alt, pie de foto)
            ("Beach volleyball at sunset", "Sunset games"),
            ("Founders working together", "Deep work days"),
            ("Campfire with the group", "Campfire talks"),
            ("Morning yoga session", "Morning flow"),
            ("Laughing during a session", "Mastermind"),
            ("Friends hugging at sunset", "The family"),
            ("Hiking in the mountains", "Hike day"),
            ("Community event", "Community night"),
            ("Night campfire", "Late nights"),
            ("Group working on laptops", "Co-working"),
        ],
        "how_title": "How we work",
        "offerings": [  # (nombre, descripción)
            ("Founder Houses",
             "Thoughtfully facilitated retreats. Curated for play, connection and breakthroughs."),
            ("Weekly Calls",
             "Weekly Accountability Calls & Monthly Community Hangouts. Stay accountable, keep momentum. "
             "Share wins, get help when you're stuck and connect with the family."),
            ("Online Platform",
             "Central online hub for the community, access curated resources, tools, and frameworks "
             "to support your growth."),
            ("Workshops",
             "Live founder talks and workshops focused on real-world lessons, practical strategies, "
             "and honest behind-the-scenes insights."),
            ("Mentorship",
             "Book 1on1 calls with people that have been through the journey."),
        ],
        "booking_title": "Pick your dates",
        "booking_subtitle": "Groups of {capacity} people. See what's happening each day, how many spots are "
                            "left and select your check-in and check-out.",
        "testimonials_title": "Meet the Family",
        "testimonials": [  # (cargo, testimonio)
            ("Founder of StudioLaar",
             "I traded irregular income and client chasing for a stable retainer client "
             "in just 2 months with the Kinhaus family."),
            ("Founder of Timmer Media",
             "I loved what I was building, but it wasn't making money yet. After joining, I first secured "
             "3 paying clients in a month to create income, which allowed me to fully focus on my main business."),
            ("Founder of North of Now",
             "I went from burning out on a single demanding client to thriving with 2 dream clients."),
            ("Founder of Okeano",
             "I went from feeling lost on what step to take next. To going all in on my passion, "
             "hosting 4 storytelling workshops in a month."),
            ("Founder of Hof van Metamorfose",
             "I had the idea, but couldn't get it out. After joining, I launched my site, started posting "
             "consistently on YouTube & IG and welcomed my first community members."),
        ],
        "faq_title": "FAQ",
        "faq": [  # (pregunta, [párrafos de respuesta])
            ("What if I'm just starting out?", [
                "Perfect. This community is for people who are serious about leveling up, whether you're just "
                "getting started or already on your way. We focus on helping you grow both your business and "
                "yourself, step by step.",
            ]),
            ("What if I don't have much money yet?", [
                "That's exactly why this exists. The goal of the community is to help you build momentum, "
                "clarity, and income, not to drain your wallet.",
            ]),
            ("What if I didn't get any value out of it?", [
                "If you show up, join the sessions, and genuinely put in the work, and after a year you feel you "
                "didn't make meaningful progress, we'll refund you in full!",
            ]),
            ("How much time does this take per week?", [
                "On average 1-2 hours a week.",
                "You get out what you put in, but this is designed to fit alongside a busy life or business.",
            ]),
            ("What are Kinhaus's core values?", [
                "1. Playfulness 2. Growth 3. Connection 4. Authenticity 5. Awareness",
            ]),
            ("Is it only online?", [
                "No, it is a hybrid community. Since members live all over the world there are online sessions. "
                "But at the heart there are the founder houses, which are intimate 1-4 week retreats.",
            ]),
        ],
        "newsletter_title": "Get the latest updates",
        "newsletter_placeholder": "yourmail@gmail.com",
        "newsletter_button": "Stay up to date",
        "social": ["More vibes", "Follow the journey"],
        "ui": {
            "language_nav": "Language",
            "theme_toggle": "Switch between light and dark mode",
            "subscribed": "Thanks! You're subscribed.",
            "already_subscribed": "This email is already subscribed.",
            "invalid_email": "Please enter a valid email.",
            "network_error": "Couldn't send it. Please try again.",
        },
    },
    "es": {
        "language_name": "Español",
        "meta_description": "Una comunidad privada para fundadores en fase inicial.",
        "hero_headline": ["Desconecta de la rutina", "y conecta con lo que importa."],
        "scroll_hint": "↓ desliza para saber más",
        "intro_title": "Despejarte un finde, romper con la rutina o impulsar tu idea: "
                       "aquí tienes una casa de campo y gente que te ayuda.",
        "intro_paragraphs": [
            [
                "Creemos que el crecimiento no ocurre en aislamiento.",
                "Ocurre en el entorno adecuado, con las personas adecuadas, que quieren lo mismo de la vida.",
            ],
            [
                "Por eso existimos.",
                "Para que rompas tus barreras y empieces a vivir la vida que siempre imaginaste.",
            ],
        ],
        "quote": [
            "Te conviertes en las cinco personas con las que",
            "más tiempo pasas. Elige bien.  - Jim Rohn",
        ],
        "join": "Únete a la familia",
        "experiences": [
            ("Vóley playa al atardecer", "Partidos al atardecer"),
            ("Fundadores trabajando juntos", "Días de trabajo profundo"),
            ("Hoguera con el grupo", "Charlas junto al fuego"),
            ("Sesión de yoga por la mañana", "Yoga al amanecer"),
            ("Risas durante una sesión", "Mastermind"),
            ("Amigos abrazados al atardecer", "La familia"),
            ("Ruta por la montaña", "Día de ruta"),
            ("Evento de la comunidad", "Noche de comunidad"),
            ("Hoguera de noche", "Noches largas"),
            ("Grupo trabajando con portátiles", "Coworking"),
        ],
        "how_title": "Cómo trabajamos",
        "offerings": [
            ("Casas de fundadores",
             "Retiros facilitados con cuidado. Pensados para jugar, conectar y lograr grandes avances."),
            ("Llamadas semanales",
             "Llamadas semanales de seguimiento y quedadas mensuales de la comunidad. Mantén el compromiso "
             "y el impulso. Comparte logros, pide ayuda cuando te atasques y conecta con la familia."),
            ("Plataforma online",
             "El punto de encuentro online de la comunidad: recursos, herramientas y metodologías "
             "seleccionadas para impulsar tu crecimiento."),
            ("Talleres",
             "Charlas y talleres en directo con fundadores: lecciones reales, estrategias prácticas "
             "y lo que pasa entre bastidores, contado con honestidad."),
            ("Mentoría",
             "Reserva llamadas 1 a 1 con personas que ya han recorrido el camino."),
        ],
        "booking_title": "Elige tus fechas",
        "booking_subtitle": "Grupos de {capacity} personas. Mira qué eventos hay cada día, cuántas plazas "
                            "quedan y marca tu llegada y tu salida.",
        "testimonials_title": "Conoce a la familia",
        "testimonials": [
            ("Fundadora de StudioLaar",
             "Cambié los ingresos irregulares y perseguir clientes por un cliente fijo mensual "
             "en solo 2 meses con la familia Kinhaus."),
            ("Fundador de Timmer Media",
             "Me encantaba lo que estaba construyendo, pero aún no generaba dinero. Al unirme, primero conseguí "
             "3 clientes de pago en un mes para tener ingresos, y eso me permitió centrarme por completo "
             "en mi negocio principal."),
            ("Fundadora de North of Now",
             "Pasé de quemarme con un único cliente muy exigente a crecer con 2 clientes de ensueño."),
            ("Fundador de Okeano",
             "Pasé de sentirme perdido sin saber cuál era el siguiente paso a apostarlo todo por mi pasión, "
             "organizando 4 talleres de storytelling en un mes."),
            ("Fundador de Hof van Metamorfose",
             "Tenía la idea, pero no conseguía sacarla. Al unirme, lancé mi web, empecé a publicar con "
             "constancia en YouTube e IG y di la bienvenida a los primeros miembros de mi comunidad."),
        ],
        "faq_title": "Preguntas frecuentes",
        "faq": [
            ("¿Y si estoy empezando?", [
                "Perfecto. Esta comunidad es para personas que van en serio con subir de nivel, tanto si acabas "
                "de empezar como si ya estás en camino. Te ayudamos a hacer crecer tu negocio y a ti, paso a paso.",
            ]),
            ("¿Y si todavía no tengo mucho dinero?", [
                "Precisamente por eso existe. El objetivo de la comunidad es ayudarte a ganar impulso, "
                "claridad e ingresos, no vaciarte la cartera.",
            ]),
            ("¿Y si no me aporta nada?", [
                "Si te presentas, asistes a las sesiones y te implicas de verdad, y después de un año sientes "
                "que no has avanzado de forma significativa, ¡te devolvemos todo el dinero!",
            ]),
            ("¿Cuánto tiempo requiere a la semana?", [
                "De media, 1-2 horas a la semana.",
                "Recibes lo que aportas, pero está pensado para encajar en una vida o un negocio con mucho ritmo.",
            ]),
            ("¿Cuáles son los valores de Kinhaus?", [
                "1. Juego 2. Crecimiento 3. Conexión 4. Autenticidad 5. Consciencia",
            ]),
            ("¿Es solo online?", [
                "No, es una comunidad híbrida. Como los miembros viven por todo el mundo, hay sesiones online. "
                "Pero el corazón son las casas de fundadores: retiros íntimos de 1 a 4 semanas.",
            ]),
        ],
        "newsletter_title": "Recibe las últimas novedades",
        "newsletter_placeholder": "tuemail@gmail.com",
        "newsletter_button": "Mantenerme al día",
        "social": ["Más vibes", "Sigue el viaje"],
        "ui": {
            "language_nav": "Idioma",
            "theme_toggle": "Cambiar entre modo claro y oscuro",
            "subscribed": "¡Gracias! Ya estás suscrito.",
            "already_subscribed": "Este email ya estaba suscrito.",
            "invalid_email": "Introduce un email válido.",
            "network_error": "No se pudo enviar. Inténtalo de nuevo.",
        },
    },
}


# ---------------------------------------------------------------------------
# Estructuras que reciben las vistas
# ---------------------------------------------------------------------------
@dataclass
class Link:
    label: str
    url: str


@dataclass
class Language:
    code: str
    name: str
    active: bool


@dataclass
class Hero:
    headline: list[str]
    image: str
    video: str | None
    scroll_hint: str


@dataclass
class Intro:
    title: str
    paragraphs: list[list[str]]
    quote: list[str]


@dataclass
class Experience:
    """Foto de una experiencia vivida (aparece en el anillo 3D)."""
    src: str
    alt: str
    caption: str


@dataclass
class Offering:
    """Pestaña de la sección 'Cómo trabajamos'."""
    slug: str
    name: str
    description: str
    image: str


@dataclass
class HowWeMove:
    title: str
    offerings: list[Offering]


@dataclass
class Booking:
    """Textos del calendario de fechas del inicio."""
    title: str
    subtitle: str


@dataclass
class Testimonial:
    name: str
    flag: str
    role: str
    quote: str
    avatar: str


@dataclass
class FaqItem:
    question: str
    answer: list[str]


@dataclass
class Footer:
    newsletter_title: str
    newsletter_placeholder: str
    newsletter_button: str
    social: list[Link]
    email: str


@dataclass
class Layout:
    """Lo común a todas las páginas: idioma, marca, controles y botón de unirse."""
    lang: str
    languages: list[Language]
    brand: str
    meta_description: str
    join_label: str
    ui: dict[str, str]


@dataclass
class HomeContent:
    hero: Hero
    intro: Intro
    experiences: list[Experience]
    how_we_move: HowWeMove
    booking: Booking
    testimonials_title: str
    testimonials: list[Testimonial]
    faq_title: str
    faq: list[FaqItem]
    footer: Footer


def get_ui_text(lang: str, key: str) -> str:
    """Texto suelto de la interfaz (mensajes de la newsletter, etiquetas…)."""
    return TEXTS.get(lang, TEXTS[DEFAULT_LANGUAGE])["ui"][key]


def get_layout(lang: str = DEFAULT_LANGUAGE) -> Layout:
    t = TEXTS[lang]
    return Layout(
        lang=lang,
        languages=[Language(code, TEXTS[code]["language_name"], code == lang) for code in SUPPORTED_LANGUAGES],
        brand=BRAND,
        meta_description=t["meta_description"],
        join_label=t["join"],
        ui=t["ui"],
    )


def get_home_content(lang: str = DEFAULT_LANGUAGE) -> HomeContent:
    t = TEXTS[lang]
    hero_folder, hero_name, hero_fallback = HERO_PHOTO

    return HomeContent(
        hero=Hero(
            t["hero_headline"],
            local_image(hero_folder, hero_name, unsplash(hero_fallback, 2000)),
            HERO_VIDEO,
            t["scroll_hint"],
        ),
        intro=Intro(t["intro_title"], t["intro_paragraphs"], t["quote"]),
        experiences=[
            Experience(unsplash(photo, 500, 500), alt, caption)
            for photo, (alt, caption) in zip(EXPERIENCE_PHOTOS, t["experiences"], strict=True)
        ],
        how_we_move=HowWeMove(
            title=t["how_title"],
            offerings=[
                Offering(slug, name, description,
                         local_image("como-nos-movemos", local_name, unsplash(fallback, 1000, 800)))
                for (slug, local_name, fallback), (name, description)
                in zip(OFFERINGS, t["offerings"], strict=True)
            ],
        ),
        booking=Booking(t["booking_title"], t["booking_subtitle"].format(capacity=GROUP_SIZE)),
        testimonials_title=t["testimonials_title"],
        testimonials=[
            Testimonial(name, flag, role, quote, unsplash(avatar, 160, 160))
            for (name, flag, avatar), (role, quote) in zip(PEOPLE, t["testimonials"], strict=True)
        ],
        faq_title=t["faq_title"],
        faq=[FaqItem(question, answer) for question, answer in t["faq"]],
        footer=Footer(
            newsletter_title=t["newsletter_title"],
            newsletter_placeholder=t["newsletter_placeholder"],
            newsletter_button=t["newsletter_button"],
            social=[Link(label, url) for label, url in zip(t["social"], SOCIAL_URLS, strict=True)],
            email=EMAIL,
        ),
    )
