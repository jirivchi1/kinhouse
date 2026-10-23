# Kinhaus: landing en Flask (MVC)

Réplica del diseño de thefounderspace.co, hecha con Flask + HTML/CSS + JS vanilla (sin React ni build).

## Arrancar

```bash
pip install -r requirements.txt
python run.py          # http://127.0.0.1:5000  (redirige a /en/ o /es/)
```

## Estructura (Modelo, Vista, Controlador)

```
run.py                          punto de entrada
config.py                       configuración
app/
  __init__.py                   create_app(): registra los controladores
  models/
    site_content.py             MODELO: todos los textos, imágenes, testimonios y FAQ
    availability.py             MODELO: fechas que se pueden reservar
    events.py                   MODELO: eventos de cada día del calendario
    application.py              MODELO: formulario de solicitud (preguntas, validación, guardado)
    subscriber.py               MODELO: suscriptores de la newsletter (data/subscribers.json)
  controllers/
    main_controller.py          CONTROLADOR: GET / (elige idioma), GET /<lang>/ y POST /subscribe
    join_controller.py          CONTROLADOR: POST /<lang>/join/ (solicitud) y página de gracias
  views/                        VISTAS (Jinja2)
    base.html, index.html, join_thanks.html
    partials/_controls (idioma + tema), _hero, _intro, _booking (calendario), _experiences,
             _how_we_move, _testimonials, _faq, _footer, _cta, _join_dialog (formulario), _form_field
  static/
    css/main.css                estilos (variables de color y fuentes arriba del todo)
    js/calendar.js              calendario del mes y formulario emergente
    js/cylinder-ring.js         anillo 3D de polaroids (experiencias)
    js/main.js                  modo claro/oscuro, pestañas y newsletter
```

## Cambiar contenido

Edita solo `app/models/site_content.py`:

- Nombre, email y enlaces: constantes `BRAND`, `EMAIL`, `APPLY_URL`, `FOUNDER_HOUSES_URL`, `SOCIAL_URLS`.
- Textos: `TEXTS["en"]` y `TEXTS["es"]`. Las listas van en el mismo orden que las fotos/personas
  (`EXPERIENCE_PHOTOS`, `OFFERINGS`, `PEOPLE`). Si falta o sobra un elemento, Python avisa con un error.
- Para añadir otro idioma: añade su código a `SUPPORTED_LANGUAGES` y un bloque `TEXTS["xx"]`.
- `EXPERIENCE_PHOTOS`: fotos del anillo 3D. Con 8 o más fotos el anillo queda completo.
- `HERO_VIDEO`: pon la URL de un `.mp4` (por ejemplo `/static/video/hero.mp4`) para usar un vídeo de fondo como en el original.

## Fotos propias

Van en `app/static/img/`, una carpeta por sección. Si la foto existe se usa; si no, se queda la de Unsplash.
Vale cualquier extensión (`.jpg`, `.jpeg`, `.png`, `.webp`, `.avif`), en mayúsculas o minúsculas.

| Sección | Carpeta | Nombres |
|---|---|---|
| Portada | `img/portada/` | `portada` |
| Cómo trabajamos (pestañas) | `img/como-nos-movemos/` | `casas_fundadores` (ya subida), `llamadas_semanales`, `plataforma_online`, `talleres`, `mentoria` |
| Anillo de experiencias | `img/experiencias/` | (pendiente de conectar) |
| Testimonios (caras) | `img/familia/` | (pendiente de conectar) |

Tamaño recomendado: pestañas 1000×800 px, actividades 600×450 px, portada 2000 px de ancho. Para que la web cargue rápido, que cada foto pese menos de 500 KB.

## Solicitudes ("Únete a la familia")

Se eligen las fechas en el calendario del inicio y el botón "Únete a la familia" abre el formulario encima de
la página. Se envía a `POST /es/join/` (o `/en/join/`); si falta algo, vuelve al inicio con el formulario abierto.
Cada solicitud se guarda como un archivo en
`data/applications/AAAAMMDD-HHMMSS_<id>.json`, con `status: "pending"`. La carpeta `data/` no se sube a git
porque contiene datos personales. Las preguntas están en `app/models/application.py` (`SECTIONS` y `FORM_TEXTS`).

## Anillo 3D (`data-cylinder-ring`)

Atributos opcionales en `_experiences.html`:
`data-duration` (segundos por vuelta), `data-tilt` (inclinación en grados), `data-perspective` (px).
Se mueve con el ratón (inclina y acelera), se puede arrastrar y respeta `prefers-reduced-motion`.
Sin JavaScript se muestra como una tira horizontal de polaroids.

## Fuentes

| Original | Usada aquí (Google Fonts) |
|---|---|
| Providence Sans (comercial) | Patrick Hand |
| Glacial Indifference | Questrial |
| Figtree / Inter | Figtree / Inter |

Si tienes licencia de Providence Sans, instálala o añade su `@font-face` y se usará automáticamente (ya está la primera en `--font-hand`).

## Idioma y modo claro/oscuro

- Arriba a la derecha hay un selector EN/ES (cada idioma tiene su URL: `/en/`, `/es/`). La elección se guarda
  en una cookie; la primera vez se usa el idioma del navegador.
- El botón sol/luna cambia el tema. Se recuerda en el navegador; si no se ha elegido, sigue el modo del sistema.
  Los colores de cada modo están como variables al principio de `main.css` (`:root` y `:root[data-theme="dark"]`).

## Testimonios

Se mueven solos de derecha a izquierda en bucle y se paran al pasar el ratón. La velocidad depende del número
de testimonios (10 s por tarjeta, en `_testimonials.html`). Con "reducir movimiento" activado en el sistema,
se quedan quietos con scroll horizontal.

## Calendario del inicio ("Elige tus fechas")

Va justo antes del anillo de fotos. Es un mes completo en cuadros con los eventos de cada día (en el móvil, un
punto en el día y la lista de eventos debajo). Primer clic: llegada; segundo clic: salida. Con las dos fechas se
activa "Únete a la familia", que abre el formulario. Las fechas se comprueban también en el servidor.

Disponibilidad, en `app/models/availability.py`:

- `BLOCKED_RANGES`: rangos de noches no disponibles `("AAAA-MM-DD", "AAAA-MM-DD")`, ambos incluidos.
  Hay uno de ejemplo (Navidad): cámbialo o bórralo.
- `BOOKING_WINDOW_DAYS`: hasta cuántos días en el futuro se puede reservar (365).
- `MIN_NIGHTS` / `MAX_NIGHTS`: duración mínima y máxima (1 y 90 noches).

Eventos, en `app/models/events.py`:

- `WEEKLY_PROGRAM`: los eventos de viernes, sábado y domingo. Va rotando: una semana la primera fila, la
  siguiente la segunda, y así. Las horas están en `EVENTS` y los nombres en `TEXTS`.
- `SPECIAL_EVENTS`: eventos sueltos en un día concreto, p. ej. `{"2026-12-05": ["bbq"]}`.

Plazas (grupos de 6), en `app/models/availability.py`:

- `GROUP_SIZE`: plazas por noche (6). Cada día del calendario muestra las que quedan ("4 plazas", "¡Quedan 2!",
  "¡Última plaza!", "Completo"), y al elegir fechas la barra dice cuántas quedan en todas esas noches.
- Cada solicitud enviada ocupa 1 plaza cada noche de su estancia, aunque esté pendiente. Si cambias su
  `"status"` a `"rejected"` en el JSON, la plaza vuelve a quedar libre. El servidor no deja apuntarse a una noche
  completa (por si dos personas lo intentan a la vez).
- `EXAMPLE_STAYS` son estancias inventadas para ver el calendario con plazas ocupadas. Cuando empieces a recibir
  solicitudes de verdad, pon `USE_EXAMPLE_DATA = False`.

Cada solicitud guarda `check_in`, `check_out`, `nights` e `info_pack_sent: false`. El info pack se envía a mano
por ahora: cuando lo mandes, cambia `info_pack_sent` a `true` en el JSON.
