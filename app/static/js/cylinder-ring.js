/**
 * CylinderRing — anillo 3D giratorio de tarjetas (versión vanilla JS del
 * componente React "Cylinder3DRing", sin React ni GSAP).
 *
 * Uso en HTML:
 *   <div data-cylinder-ring data-duration="28" data-tilt="-12">
 *     <figure>…</figure>   (una tarjeta por hijo)
 *   </div>
 *
 * - Gira de forma continua (una vuelta cada `duration` segundos).
 * - Con el ratón: inclina el anillo y acelera/invierte el giro.
 * - Con el dedo o arrastrando: gira el anillo manualmente.
 */
(function () {
  "use strict";

  const MIN_CARDS = 8;
  const lerp = (a, b, t) => a + (b - a) * t;

  class CylinderRing {
    constructor(stage, options = {}) {
      this.stage = stage;
      this.duration = Number(stage.dataset.duration || options.duration || 18);
      this.baseTilt = Number(stage.dataset.tilt || options.tilt || -14);
      this.perspective = Number(stage.dataset.perspective || options.perspective || 1100);
      this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      this.sources = Array.from(stage.children);
      this.angle = 0;
      this.speed = 1;          // multiplicador actual de velocidad
      this.targetSpeed = 1;
      this.tiltX = this.baseTilt;
      this.tiltZ = 0;
      this.targetTiltX = this.baseTilt;
      this.targetTiltZ = 0;
      this.dragging = false;
      this.visible = true;
      this.lastTime = 0;

      this.build();
      this.bindEvents();
      requestAnimationFrame((t) => this.tick(t));
    }

    /* Tamaños adaptativos (mismas fórmulas que el componente original) */
    measure() {
      const width = this.stage.clientWidth || 800;
      const count = Math.max(this.sources.length, MIN_CARDS);

      const cardW =
        width < 420 ? Math.max(Math.round(width * 0.26), 90)
        : width < 640 ? Math.max(Math.round(width * 0.22), 110)
        : width < 1024 ? Math.min(Math.max(Math.round(width * 0.18), 130), 180)
        : Math.min(Math.max(Math.round(width * 0.16), 140), 210);
      const cardH = Math.round(cardW * 1.2); // proporción polaroid

      const spacing = width < 480 ? 12 : width < 768 ? 16 : 22;
      const scale = width < 480 ? 1.08 : width < 768 ? 1.15 : 1.22;
      const radius = Math.round(((cardW + spacing) / (2 * Math.tan(Math.PI / count))) * scale);
      const height = width < 480 ? 290 : width < 768 ? 380 : 490;

      return { width, count, cardW, cardH, radius, height };
    }

    build() {
      const m = (this.m = this.measure());
      const stage = this.stage;

      stage.classList.add("is-3d");
      stage.style.minHeight = m.height + "px";
      stage.style.perspective = (m.width < 640 ? Math.min(this.perspective, 850) : this.perspective) + "px";

      this.tilt = document.createElement("div");
      this.tilt.className = "ring__tilt";
      this.drum = document.createElement("div");
      this.drum.className = "ring__drum";
      this.drum.style.width = m.cardW + "px";
      this.drum.style.height = m.cardH + "px";

      this.cards = [];
      for (let i = 0; i < m.count; i++) {
        const card = this.sources[i % this.sources.length].cloneNode(true);
        const angle = (360 / m.count) * i;
        card.style.transform = `rotateY(${angle}deg) translateZ(${m.radius}px)`;
        card.setAttribute("aria-hidden", i >= this.sources.length ? "true" : "false");
        this.drum.appendChild(card);
        this.cards.push({ el: card, angle, back: false });
      }

      this.tilt.appendChild(this.drum);
      stage.replaceChildren(this.tilt);
      this.render();
    }

    rebuild() {
      const m = this.measure();
      if (this.m && m.width === this.m.width) return;
      this.build();
    }

    bindEvents() {
      const stage = this.stage;

      stage.addEventListener("pointermove", (e) => {
        const rect = stage.getBoundingClientRect();
        const normX = (e.clientX - rect.left) / rect.width - 0.5;
        const normY = (e.clientY - rect.top) / rect.height - 0.5;

        if (this.dragging) {
          // Arrastrar gira el anillo directamente
          this.angle -= (e.clientX - this.lastX) * 0.35;
          this.lastX = e.clientX;
          return;
        }
        if (e.pointerType !== "mouse") return;

        this.targetTiltX = this.baseTilt - normY * 16;
        this.targetTiltZ = normX * 4;
        // A la derecha acelera, a la izquierda invierte el giro
        this.targetSpeed = 1 + normX * 3.5;
      });

      stage.addEventListener("pointerdown", (e) => {
        this.dragging = true;
        this.lastX = e.clientX;
        this.targetSpeed = 0;
        stage.classList.add("is-dragging");
        stage.setPointerCapture(e.pointerId);
      });

      const release = () => {
        if (this.dragging) {
          this.dragging = false;
          stage.classList.remove("is-dragging");
        }
        this.targetSpeed = 1;
      };
      stage.addEventListener("pointerup", release);
      stage.addEventListener("pointercancel", release);

      stage.addEventListener("pointerleave", () => {
        release();
        this.targetTiltX = this.baseTilt;
        this.targetTiltZ = 0;
      });

      // Reconstruye al cambiar el ancho (con debounce)
      let timer;
      new ResizeObserver(() => {
        clearTimeout(timer);
        timer = setTimeout(() => this.rebuild(), 150);
      }).observe(stage);

      // Pausa la animación cuando no está en pantalla
      new IntersectionObserver(([entry]) => {
        this.visible = entry.isIntersecting;
      }).observe(stage);
    }

    tick(time) {
      const dt = Math.min((time - this.lastTime) / 1000 || 0, 0.05);
      this.lastTime = time;

      if (this.visible) {
        const baseVelocity = this.reducedMotion ? 0 : 360 / this.duration; // grados/segundo
        this.speed = lerp(this.speed, this.targetSpeed, 0.06);
        this.tiltX = lerp(this.tiltX, this.targetTiltX, 0.08);
        this.tiltZ = lerp(this.tiltZ, this.targetTiltZ, 0.08);
        this.angle += baseVelocity * this.speed * dt;
        this.render();
      }
      requestAnimationFrame((t) => this.tick(t));
    }

    render() {
      const r = this.m.radius;
      this.tilt.style.transform =
        `translateZ(${-r * 0.32}px) rotateX(${this.tiltX}deg) rotateZ(${this.tiltZ}deg)`;
      this.drum.style.transform = `rotateY(${-this.angle}deg)`;

      // Marca las tarjetas que quedan de espaldas (se atenúan por CSS)
      for (const card of this.cards) {
        const back = Math.cos(((card.angle - this.angle) * Math.PI) / 180) < -0.05;
        if (back !== card.back) {
          card.back = back;
          card.el.classList.toggle("is-back", back);
        }
      }
    }
  }

  window.CylinderRing = CylinderRing;

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-cylinder-ring]").forEach((el) => new CylinderRing(el));
  });
})();
