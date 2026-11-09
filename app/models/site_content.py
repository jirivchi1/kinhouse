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

from app.models.availability import STAY_PRICE_PER_DAY

SUPPORTED_LANGUAGES = ("en", "es")
DEFAULT_LANGUAGE = "en"

BRAND = "Kinhaus"
EMAIL = "hi@kinhaus.co"
SOCIAL_URLS = ["https://www.instagram.com/", "https://www.youtube.com/"]

IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".webm"}


def unsplash(photo_id: str, width: int = 800, height: int | None = None) -> str:
    """URL de una imagen de Unsplash recortada al tamaño pedido."""
    url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={width}&q=80"
    if height:
        url += f"&h={height}"
    return url


def format_price(amount: int, lang: str) -> str:
    """10 -> '10 €' en español, '€10' en inglés."""
    return f"{amount} €" if lang == "es" else f"€{amount}"


def local_image(folder: str, name: str, fallback: str | None, extensions: set = IMAGE_EXTENSIONS) -> str | None:
    """Foto propia de app/static/img/<folder>/<name>.<jpg|jpeg|png|webp|avif>.

    Si no existe, devuelve `fallback` (la foto de Unsplash). No importa la
    extensión ni las mayúsculas. El ?v= hace que el navegador recargue la
    foto cuando la sustituyes por otra con el mismo nombre.
    """
    directory = IMG_DIR / folder
    if directory.is_dir():
        for file in directory.iterdir():
            if file.stem.lower() == name.lower() and file.suffix.lower() in extensions:
                return f"/static/img/{folder}/{file.name}?v={int(file.stat().st_mtime)}"
    return fallback


# ---------------------------------------------------------------------------
# Datos que no cambian con el idioma
# ---------------------------------------------------------------------------
HERO_PHOTO = ("portada", "portada", "1600596542815-ffad4c1539a9")  # (carpeta, nombre, reserva)
HERO_VIDEO = "portada.mp4"  # vídeo en bucle de img/portada/ (sin sonido); si no existe, se usa la foto

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

# "Recuerdos de los fines de semana": (foto propia en img/recuerdos/, foto de reserva)
MEMORIES = [
    ("cata_vinos", "1558670460-cad0c19b1840"),
    ("ruta_caballo", "1771102768656-87d4e54e9a48"),
    ("yoga_animales", "1634140325686-b507b470e48a"),
    ("playa", "1767206105936-468e76a69fe4"),
    ("vacas_quesos", "1596733430284-f7437764b1a9"),
    ("barbacoa", "1579405317876-9340f1d26061"),
]

# "Quién está detrás": foto propia en img/informacion/ismael.(jpg|png…). Sin foto se ven las iniciales.
ABOUT_PHOTO = ("informacion", "ismael")

# "Dónde estamos": mapa en img/informacion/mapa_web.jpg (versión ligera de mapa.jpg)
MAP_PHOTO = ("informacion", "mapa_web")
# Tiempos en coche desde la casa (los nombres van traducidos en TEXTS[...]["places"])
PLACE_MINUTES = [5, 10, 10, 12, 20]

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
        "meta_description": "Different weekend plans at a country house in Elche (Alicante, Spain): unplug and "
                            "meet curious, driven people.",
        "hero_headline": ["Unplug from the routine,", "reconnect with what matters."],
        "scroll_hint": "↓ scroll to learn more",
        "hero_location": "Country house · Elche (Alicante, Spain)",
        "intro_title": "Different weekend plans at a country house in Elche: unplug and meet curious, driven people.",
        "intro_paragraphs": [
            [
                "Every weekend we organise plans in the countryside, 12 minutes from Elche:",
                "wine tastings, horse riding, yoga with animals, barbecues by the fire…",
            ],
            [
                "You come, unplug and meet people with ideas and the drive to make things happen.",
                "And if you have a project or a business, you'll find people here to help you push it forward.",
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
        "how_it_works_title": "How it works",
        "how_it_works": [  # (título, texto) de cada paso
            ("Pick your plan",
             "Check the calendar and pick a weekend plan. Or a few days, if you're coming to work on your idea."),
            ("Save your spot", "Leave your details in a minute. You don't pay anything now."),
            ("We confirm and you come", "We email you all the details: how to get there, what to bring and how to pay."),
        ],
        "how_it_works_prices": "Plans from {from_plan} per person · Stays from {from_day} per person and day",
        "how_it_works_cta": "See the plans",
        "work_title": "Coming to work on your idea?",
        "work_subtitle": "Groups, teams and travellers from abroad who want to spend a few days in the countryside "
                         "working on their project, 20 minutes from Alicante airport. It's our next stage: if "
                         "you're interested, book a few days and we'll organise it with you.",
        "work_cta": "Book a few days",
        "how_title": "How we work on your idea or project",
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
        "booking_title": "Book a plan or a few days",
        "booking_subtitle": "Come for a weekend plan or stay a few days. "
                            "See how many spots are left and save yours in a minute.",
        "memories_title": "Weekend memories",
        "memories_subtitle": "This is what our plans look like: people arrive as strangers and leave as friends.",
        "memories": [  # pie de cada foto, en el orden de MEMORIES
            "Wine tasting",
            "Horse riding",
            "Yoga with animals",
            "Sunset at the beach",
            "Cows & cheese",
            "Barbecue & campfire",
        ],
        "testimonials_title": "Meet the Family",
        "testimonials_subtitle": "People who came for a plan, stayed and now bring what they know.",
        "testimonials": [  # (lo que aporta, su idea y su aportación)
            ("Brand designer · personal brand workshop",
             "I came for a weekend to disconnect and stayed in the family. Now I run the personal brand "
             "workshop and help others give their project a face."),
            ("Video creator · content workshop",
             "My idea was to make a living from video. Here I found my first clients, and now I teach how to "
             "film with your phone in the workshops at the house."),
            ("Coach · 1on1 mentoring",
             "I help people who are just starting to bring order to their idea. It's what I wish I'd had: "
             "someone who has already been there."),
            ("Storyteller · campfire nights",
             "The best ideas come up around the fire. I host the storytelling nights, and a new project "
             "always comes out of them."),
            ("Community builder · AI workshop",
             "I launched my community with the family's help. Now I return the favour with a workshop on AI "
             "tools for small businesses."),
        ],
        "member_title": "Want to be part of the family?",
        "member_text": "Become a member: you join the community group and can bring what you know, as a "
                       "mentor, running a workshop or helping with the plans. That's how we all grow.",
        "member_benefits": [
            "Private group with the other members",
            "Run workshops or mentoring sessions",
            "Priority on plans and stays",
            "Meet professionals with the same drive",
        ],
        "member_cta": "I want to be a member",
        "about_title": "Who's behind it",
        "about_roles": ["Developer", "Solopreneur", "Maker", "Kinhaus host"],
        "about_text": [
            "I build digital products from the countryside, and I love making things with my hands and with code.",
            "I've opened my home so people with the drive to make things have a place to unplug, meet and "
            "create. I'll be your host.",
        ],
        "location_title": "Where we are",
        "location_subtitle": "In the countryside of Elche (Alicante, Spain), between Elche and the beach.",
        "places": ["La Hoya supermarket", "La Marina beach", "El Hondo Natural Park", "Elche", "Alicante airport"],
        "location_note": "By car. We send you the exact address when we confirm your spot.",
        "minutes": "{n} min",
        "faq_title": "FAQ",
        "faq": [  # (pregunta, [párrafos de respuesta]). {from_plan} y {from_day} se rellenan solos
            ("Where is the house?", [
                "In the countryside of Elche (Alicante, Spain): 12 minutes from Elche, 10 from La Marina beach "
                "and El Hondo Natural Park, and 20 from Alicante airport. You'll find the map at the end of the page.",
            ]),
            ("How much does it cost?", [
                "Plans from {from_plan} per person. Stays from {from_day} per person and day.",
                "You see the exact price before sending your booking, and you don't pay anything until we confirm "
                "your spot.",
            ]),
            ("Do I have to stay overnight?", [
                "No. You can come just for the plan and go back home. If you want to stay a few days, choose "
                "\"A few days\" in the calendar.",
            ]),
            ("Can I come on my own?", [
                "Of course. Almost everyone comes alone: the plans are designed to meet people.",
            ]),
            ("What if I have an idea or a business?", [
                "Perfect. Many of the people who come have projects, and in the workshops and mentoring you can move "
                "yours forward. If you want to come for a few days to work on it, see \"Coming to work on your idea?\".",
            ]),
            ("What are Kinhaus's core values?", [
                "1. Playfulness 2. Growth 3. Connection 4. Authenticity 5. Awareness",
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
        "meta_description": "Planes de fin de semana distintos en una casa de campo en Elche (Alicante): "
                            "desconecta y conoce gente con inquietudes.",
        "hero_headline": ["Desconecta de la rutina", "y conecta con lo que importa."],
        "scroll_hint": "↓ desliza para saber más",
        "hero_location": "Casa de campo · Elche (Alicante)",
        "intro_title": "Planes de fin de semana distintos en una casa de campo en Elche, para desconectar y "
                       "conocer gente con inquietudes.",
        "intro_paragraphs": [
            [
                "Cada fin de semana organizamos planes en el campo, a 12 minutos de Elche:",
                "catas de vino, rutas a caballo, yoga con animales, barbacoas junto al fuego…",
            ],
            [
                "Vienes, desconectas y conoces a gente con ideas y ganas de hacer cosas.",
                "Y si tienes un proyecto o un negocio, aquí encontrarás quien te ayude a impulsarlo.",
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
        "how_it_works_title": "Cómo funciona",
        "how_it_works": [
            ("Elige tu plan",
             "Mira el calendario y elige un plan de fin de semana. O unos días, si vienes a trabajar en tu idea."),
            ("Reserva tu plaza", "Déjanos tus datos en un minuto. No pagas nada ahora."),
            ("Te confirmamos y vienes", "Te escribimos con todos los detalles: cómo llegar, qué traer y cómo pagar."),
        ],
        "how_it_works_prices": "Planes desde {from_plan} por persona · Estancias desde {from_day} por persona y día",
        "how_it_works_cta": "Ver los planes",
        "work_title": "¿Vienes a trabajar en tu idea?",
        "work_subtitle": "Grupos, equipos y viajeros de otros países que quieren pasar unos días en el campo "
                         "trabajando en su proyecto, a 20 minutos del aeropuerto de Alicante. Es nuestra siguiente "
                         "etapa: si te interesa, reserva unos días y lo organizamos contigo.",
        "work_cta": "Reservar unos días",
        "how_title": "Cómo trabajamos tu idea o proyecto",
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
        "booking_title": "Reserva un plan o unos días",
        "booking_subtitle": "Ven a un plan de fin de semana o quédate unos días. "
                            "Mira las plazas que quedan y guarda la tuya en un minuto.",
        "memories_title": "Recuerdos de los fines de semana",
        "memories_subtitle": "Así son nuestros planes: gente que llega sin conocerse y se va con amigos.",
        "memories": [
            "Cata de vinos",
            "Ruta a caballo",
            "Yoga con animales",
            "Atardecer en la playa",
            "Vacas y quesos",
            "Barbacoa y hoguera",
        ],
        "testimonials_title": "Conoce a la familia",
        "testimonials_subtitle": "Personas que vinieron a un plan, se quedaron y ahora aportan lo que saben.",
        "testimonials": [
            ("Diseñadora de marca · taller de marca personal",
             "Llegué para un finde de desconexión y me quedé en la familia. Ahora imparto el taller de marca "
             "personal y ayudo a otros a darle cara a su proyecto."),
            ("Creador de vídeo · taller de contenido",
             "Mi idea era vivir del vídeo. Aquí encontré mis primeros clientes y ahora enseño a grabar con el "
             "móvil en los talleres de la casa."),
            ("Coach · mentoría 1 a 1",
             "Acompaño a quien está empezando a ordenar su idea. Es lo que me habría gustado tener a mí: "
             "alguien que ya ha pasado por ahí."),
            ("Storyteller · noches de hoguera",
             "Las mejores ideas salen alrededor del fuego. Organizo las noches de historias y siempre sale "
             "algún proyecto nuevo."),
            ("Creador de comunidades · taller de IA",
             "Lancé mi comunidad con ayuda de la familia. Ahora devuelvo el favor con un taller de "
             "herramientas de IA para negocios pequeños."),
        ],
        "member_title": "¿Quieres ser parte de la familia?",
        "member_text": "Hazte miembro: entras en el grupo de la comunidad y puedes aportar lo que sabes, como "
                       "mentor, impartiendo un taller o ayudando con los planes. Así crecemos todos.",
        "member_benefits": [
            "Grupo privado con el resto de miembros",
            "Imparte talleres o mentorías",
            "Prioridad en planes y estancias",
            "Conoce a profesionales con tus mismas ganas",
        ],
        "member_cta": "Quiero ser miembro",
        "about_title": "Quién está detrás",
        "about_roles": ["Programador", "Solopreneur", "Maker", "Anfitrión de Kinhaus"],
        "about_text": [
            "Construyo productos digitales desde el campo y me encanta crear cosas con las manos y con código.",
            "He abierto mi casa para que la gente con ganas de hacer cosas tenga un sitio donde desconectar, "
            "conocerse y crear. Seré tu anfitrión.",
        ],
        "location_title": "Dónde estamos",
        "location_subtitle": "En el campo de Elche (Alicante), entre Elche y la playa.",
        "places": ["Supermercado La Hoya", "Playa La Marina", "Parque Natural El Hondo", "Elche",
                   "Aeropuerto de Alicante"],
        "location_note": "En coche. La dirección exacta te la enviamos al confirmar tu plaza.",
        "minutes": "{n} min",
        "faq_title": "Preguntas frecuentes",
        "faq": [
            ("¿Dónde está la casa?", [
                "En el campo de Elche (Alicante): a 12 minutos de Elche, a 10 de la playa de La Marina y del "
                "Parque Natural El Hondo, y a 20 del aeropuerto de Alicante. Tienes el mapa al final de la página.",
            ]),
            ("¿Cuánto cuesta?", [
                "Los planes, desde {from_plan} por persona. Las estancias, desde {from_day} por persona y día.",
                "Ves el precio exacto antes de enviar tu reserva y no pagas nada hasta que te confirmamos la plaza.",
            ]),
            ("¿Tengo que quedarme a dormir?", [
                "No. Puedes venir solo al plan y volver a casa. Si quieres quedarte unos días, elige «Unos días» "
                "en el calendario.",
            ]),
            ("¿Puedo venir solo o sola?", [
                "Claro. Casi todo el mundo viene solo: los planes están pensados para conocer gente.",
            ]),
            ("¿Y si tengo una idea o un negocio?", [
                "Perfecto. Mucha de la gente que viene tiene proyectos, y en los talleres y mentorías puedes avanzar "
                "en el tuyo. Si quieres venir unos días a trabajar en él, mira «¿Vienes a trabajar en tu idea?».",
            ]),
            ("¿Cuáles son los valores de Kinhaus?", [
                "1. Juego 2. Crecimiento 3. Conexión 4. Autenticidad 5. Consciencia",
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
    location: str


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
class Step:
    number: int
    title: str
    text: str


@dataclass
class HowItWorks:
    """"Cómo funciona" en 3 pasos (antes del calendario)."""
    title: str
    steps: list[Step]
    prices: str
    cta: str


@dataclass
class Work:
    """Segunda etapa: "¿Vienes a trabajar en tu idea?" (unos días, grupos) con las pestañas en pequeño."""
    title: str
    subtitle: str
    cta: str
    how_we_move: "HowWeMove"


@dataclass
class About:
    """"Quién está detrás"."""
    title: str
    name: str
    roles: list[str]
    text: list[str]
    photo: str | None
    initials: str


@dataclass
class Place:
    name: str
    time: str


@dataclass
class Location:
    """"Dónde estamos": mapa y tiempos en coche."""
    title: str
    subtitle: str
    map: str | None
    places: list[Place]
    note: str


@dataclass
class Booking:
    """Textos del calendario de fechas del inicio."""
    title: str
    subtitle: str


@dataclass
class Memory:
    """Foto de un plan de fin de semana (sección "Recuerdos")."""
    src: str
    caption: str


@dataclass
class Memories:
    title: str
    subtitle: str
    items: list[Memory]


@dataclass
class Membership:
    """Bloque "¿Quieres ser parte de la familia?" de la sección de la familia."""
    title: str
    text: str
    benefits: list[str]
    cta: str


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
    how_it_works: HowItWorks
    work: Work
    booking: Booking
    memories: Memories
    testimonials_title: str
    testimonials_subtitle: str
    testimonials: list[Testimonial]
    membership: Membership
    about: About
    location: Location
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


OWNER_NAME = "Ismael Rivera"


def get_home_content(lang: str = DEFAULT_LANGUAGE) -> HomeContent:
    # Aquí dentro para no crear una dependencia circular (events.py usa este módulo)
    from app.models.events import EVENTS

    t = TEXTS[lang]
    hero_folder, hero_name, hero_fallback = HERO_PHOTO
    prices = {
        "from_plan": format_price(min(event.price for event in EVENTS.values()), lang),
        "from_day": format_price(STAY_PRICE_PER_DAY, lang),
    }

    return HomeContent(
        hero=Hero(
            t["hero_headline"],
            local_image(hero_folder, hero_name, unsplash(hero_fallback, 2000)),
            local_image(hero_folder, Path(HERO_VIDEO).stem, None, VIDEO_EXTENSIONS) if HERO_VIDEO else None,
            t["scroll_hint"],
            t["hero_location"],
        ),
        intro=Intro(t["intro_title"], t["intro_paragraphs"], t["quote"]),
        experiences=[
            Experience(unsplash(photo, 500, 500), alt, caption)
            for photo, (alt, caption) in zip(EXPERIENCE_PHOTOS, t["experiences"], strict=True)
        ],
        how_it_works=HowItWorks(
            title=t["how_it_works_title"],
            steps=[Step(i, title, text) for i, (title, text) in enumerate(t["how_it_works"], start=1)],
            prices=t["how_it_works_prices"].format(**prices),
            cta=t["how_it_works_cta"],
        ),
        work=Work(
            title=t["work_title"],
            subtitle=t["work_subtitle"],
            cta=t["work_cta"],
            how_we_move=HowWeMove(
                title=t["how_title"],
                offerings=[
                    Offering(slug, name, description,
                             local_image("como-nos-movemos", local_name, unsplash(fallback, 1000, 800)))
                    for (slug, local_name, fallback), (name, description)
                    in zip(OFFERINGS, t["offerings"], strict=True)
                ],
            ),
        ),
        booking=Booking(t["booking_title"], t["booking_subtitle"]),
        memories=Memories(
            t["memories_title"],
            t["memories_subtitle"],
            [
                Memory(local_image("recuerdos", photo, unsplash(fallback, 700, 700)), caption)
                for (photo, fallback), caption in zip(MEMORIES, t["memories"], strict=True)
            ],
        ),
        testimonials_title=t["testimonials_title"],
        testimonials_subtitle=t["testimonials_subtitle"],
        membership=Membership(t["member_title"], t["member_text"], t["member_benefits"], t["member_cta"]),
        about=About(
            title=t["about_title"],
            name=OWNER_NAME,
            roles=t["about_roles"],
            text=t["about_text"],
            photo=local_image(*ABOUT_PHOTO, None),
            initials="".join(part[0] for part in OWNER_NAME.split()[:2]),
        ),
        location=Location(
            title=t["location_title"],
            subtitle=t["location_subtitle"],
            map=local_image(*MAP_PHOTO, None),
            places=[Place(name, t["minutes"].format(n=n)) for name, n in zip(t["places"], PLACE_MINUTES, strict=True)],
            note=t["location_note"],
        ),
        testimonials=[
            Testimonial(name, flag, role, quote, unsplash(avatar, 160, 160))
            for (name, flag, avatar), (role, quote) in zip(PEOPLE, t["testimonials"], strict=True)
        ],
        faq_title=t["faq_title"],
        faq=[FaqItem(question, [p.format(**prices) for p in answer]) for question, answer in t["faq"]],
        footer=Footer(
            newsletter_title=t["newsletter_title"],
            newsletter_placeholder=t["newsletter_placeholder"],
            newsletter_button=t["newsletter_button"],
            social=[Link(label, url) for label, url in zip(t["social"], SOCIAL_URLS, strict=True)],
            email=EMAIL,
        ),
    )
