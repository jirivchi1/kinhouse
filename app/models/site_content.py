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
VIDEO_EXTENSIONS = {".mp4", ".webm"}


def unsplash(photo_id: str, width: int = 800, height: int | None = None) -> str:
    """URL de una imagen de Unsplash recortada al tamaño pedido."""
    url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={width}&q=80"
    if height:
        url += f"&h={height}"
    return url


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
        "booking_subtitle": "Come for a plan or stay a few days in groups of {capacity}. "
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
        "booking_subtitle": "Ven a un plan o quédate unos días en grupos de {capacity}. "
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
    how_we_move: HowWeMove
    booking: Booking
    memories: Memories
    testimonials_title: str
    testimonials_subtitle: str
    testimonials: list[Testimonial]
    membership: Membership
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
            local_image(hero_folder, Path(HERO_VIDEO).stem, None, VIDEO_EXTENSIONS) if HERO_VIDEO else None,
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
