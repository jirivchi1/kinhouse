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
    subscriber.py               MODELO: suscriptores de la newsletter (data/subscribers.json)
  controllers/
    main_controller.py          CONTROLADOR: GET / (elige idioma), GET /<lang>/ y POST /subscribe
  views/                        VISTAS (Jinja2)
    base.html, index.html
    partials/_controls (idioma + tema), _hero, _intro, _experiences, _how_we_move,
             _testimonials, _faq, _footer, _cta
  static/
    css/main.css                estilos (variables de color y fuentes arriba del todo)
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
- Las imágenes son de Unsplash. Para usar fotos propias, ponlas en `app/static/img/` y usa `/static/img/foto.jpg`.

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
