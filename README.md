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
| Recuerdos de los fines de semana | `img/recuerdos/` | `cata_vinos`, `ruta_caballo`, `yoga_animales`, `playa`, `vacas_quesos`, `barbacoa` |
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

## Calendario del inicio: "Un plan" o "Unos días"

Va justo después del anillo de fotos. Arriba tiene dos pestañas (como Airbnb con alojamientos y experiencias)
para que cada persona diga qué quiere:

- **Un plan**: cada día con plan muestra hora, nombre y plazas que quedan ("quedan 3"). Al tocar el día, la
  barra de abajo enseña el plan y "Reservar plaza" abre el formulario.
- **Unos días**: primer clic llegada, segundo clic último día (el mismo si es solo uno). Se reserva y se cobra
  **por día**, ambos incluidos: del 8 al 12 son 5 días. Cada día muestra las plazas libres del grupo de 6.

Al reservar unos días, el formulario enseña los planes que caen dentro de la estancia (p. ej. de viernes a domingo)
para apuntarse. Se guardan en `stay_events` y ocupan plaza en el plan igual que una reserva suelta.

**El precio no sale en el calendario**: solo aparece dentro del formulario, cuando ya han elegido, con el total
según las personas y la frase "No pagas nada ahora". Así el precio no frena antes de tiempo.

Para quitar la pestaña "Unos días", pon `STAYS_ENABLED = False` en `app/models/availability.py`.

Planes, en `app/models/events.py`:

- `EVENTS`: cada plan con hora, precio por persona y plazas. Los nombres están en `TEXTS`.
- `WEEKLY_PROGRAM`: los planes de viernes, sábado y domingo. Va rotando: una semana la primera fila, la
  siguiente la segunda, y así. Las fechas se calculan solas.
- `SPECIAL_EVENTS`: planes sueltos en un día concreto, p. ej. `{"2026-12-05": ["bbq"]}`.
- `EXAMPLE_BOOKINGS`: reservas inventadas para ver plazas ocupadas. Pon `USE_EXAMPLE_DATA = False` cuando
  empieces con reservas de verdad.
- Cada reserva enviada ocupa tantas plazas como personas apunta. Si cambias su `"status"` a `"rejected"`, las
  plazas vuelven. El servidor no deja reservar más plazas de las que quedan.

Estancias por días, en `app/models/availability.py`:

- `STAY_PRICE_PER_DAY`: precio por persona y día (20 €). Solo se ve en el formulario.
- `BLOCKED_RANGES`: días cerrados `("AAAA-MM-DD", "AAAA-MM-DD")`, ambos incluidos.
  Hay uno de ejemplo (Navidad): cámbialo o bórralo.
- `BOOKING_WINDOW_DAYS`: hasta cuántos días en el futuro se puede reservar (365).
- `MIN_DAYS` / `MAX_DAYS`: duración mínima y máxima (1 y 90 días).

Plazas (grupos de 6), en `app/models/availability.py`:

- `GROUP_SIZE`: plazas por día (6). Cada día del calendario muestra las que quedan ("4 plazas", "¡Quedan 2!",
  "¡Última plaza!", "Completo"), y al elegir fechas la barra dice cuántas quedan en todos esos días.
- Cada solicitud enviada ocupa tantas plazas como personas apunta cada día de su estancia, aunque esté pendiente. Si cambias su
  `"status"` a `"rejected"` en el JSON, la plaza vuelve a quedar libre. El servidor no deja apuntarse a un día
  completo (por si dos personas lo intentan a la vez).
- `EXAMPLE_STAYS` son estancias inventadas para ver el calendario con plazas ocupadas. Cuando empieces a recibir
  solicitudes de verdad, pon `USE_EXAMPLE_DATA = False`.

Cada solicitud guarda `type` (`event` o `stay`), el plan o los días (`check_in`, `check_out`, `days`), `people` e `info_pack_sent: false`. El info pack se envía a mano
por ahora: cuando lo mandes, cambia `info_pack_sent` a `true` en el JSON.

## Recuerdos, familia y miembros (inicio)

- **Recuerdos de los fines de semana** (entre el calendario y "Cómo trabajamos tu idea o proyecto"): 6 fotos de los
  planes. Pon las tuyas en `img/recuerdos/` con los nombres de la tabla. Pies de foto en `TEXTS[...]["memories"]`.
- **Conoce a la familia**: miembros que cuentan su idea y lo que aportan (`TEXTS[...]["testimonials"]`, que son
  ejemplos: cámbialos por personas reales). Debajo está el bloque **"¿Quieres ser parte de la familia?"**
  (`member_title`, `member_text`, `member_benefits`, `member_cta`).
- **Quiero ser miembro** abre su propio formulario (`MEMBER_SECTIONS` en `app/models/application.py`): a qué se
  dedica, cómo le gustaría aportar (taller, mentoría, planes…) y algo más sobre su idea. Se envía a
  `POST /<lang>/member/` y se guarda en `data/applications/` con `"type": "member"`. No ocupa plazas.
