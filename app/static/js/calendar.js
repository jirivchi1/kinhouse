/**
 * Calendario del mes con eventos (sección "Elige tus fechas" del inicio). Sin librerías.
 *
 * Lee data-config (lo prepara main_controller.booking_calendar):
 *   { min, max, blocked: ["AAAA-MM-DD"], capacity, taken: {"AAAA-MM-DD": personas},
 *     minNights, maxNights, lang, labels, events: {"AAAA-MM-DD": [[hora, nombre], …]} }
 *
 * - Cada día muestra las plazas libres esa noche (capacity - taken).
 * - Primer clic: día de llegada. Segundo clic: día de salida.
 * - Las noches cerradas o completas salen tachadas y no se pueden cruzar.
 * - "Únete a la familia" abre el formulario (<dialog>) con las fechas ya puestas.
 */
(function () {
  "use strict";

  const DAY = 86400000;
  // Trabajamos siempre en UTC para que la zona horaria no mueva los días
  const parse = (iso) => {
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(Date.UTC(y, m - 1, d));
  };
  const toIso = (date) => date.toISOString().slice(0, 10);
  const addDays = (date, n) => new Date(date.getTime() + n * DAY);
  const daysBetween = (a, b) => Math.round((b - a) / DAY);
  const monthStart = (date) => new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
  const isIso = (value) => /^\d{4}-\d{2}-\d{2}$/.test(value || "");
  const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);
  const escape = (text) => text.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

  class MonthCalendar {
    constructor(root) {
      this.root = root;
      this.cfg = JSON.parse(root.dataset.config);
      this.t = this.cfg.labels;
      this.min = parse(this.cfg.min);
      this.max = parse(this.cfg.max);
      this.today = this.min;
      this.blocked = new Set(this.cfg.blocked);
      this.dialog = document.querySelector(root.dataset.dialog);
      this.inInput = this.dialog.querySelector("[data-check-in]");
      this.outInput = this.dialog.querySelector("[data-check-out]");
      this.hover = null;

      const tz = { timeZone: "UTC" };
      this.fmtMonth = new Intl.DateTimeFormat(this.cfg.lang, { month: "long", year: "numeric", ...tz });
      this.fmtMonthName = new Intl.DateTimeFormat(this.cfg.lang, { month: "long", ...tz });
      this.fmtShort = new Intl.DateTimeFormat(this.cfg.lang, { day: "numeric", month: "short", year: "numeric", ...tz });
      this.fmtLong = new Intl.DateTimeFormat(this.cfg.lang, { weekday: "long", day: "numeric", month: "long", ...tz });
      this.fmtWeekday = new Intl.DateTimeFormat(this.cfg.lang, { weekday: "short", ...tz });

      // Si el formulario vuelve con errores, recupera las fechas que ya estaban
      const savedIn = this.inInput.value;
      const savedOut = this.outInput.value;
      this.checkIn = isIso(savedIn) && this.canCheckIn(parse(savedIn)) ? parse(savedIn) : null;
      this.checkOut = this.checkIn && isIso(savedOut) && this.canCheckOut(parse(savedOut)) ? parse(savedOut) : null;
      this.view = monthStart(this.checkIn || this.min);

      this.build();
      this.render();
      this.initDialog();
    }

    /* ---------- Reglas ---------- */
    /** Plazas libres la noche que empieza ese día. */
    free(iso) {
      return Math.max(this.cfg.capacity - (this.cfg.taken[iso] || 0), 0);
    }

    /** Noche que no se puede reservar: casa cerrada o grupo completo. */
    unavailable(iso) {
      return this.blocked.has(iso) || this.free(iso) === 0;
    }

    canCheckIn(date) {
      return date >= this.min && date < this.max && !this.unavailable(toIso(date));
    }

    /** Última salida posible: el primer día sin plaza tras la llegada (esa noche ya no está libre). */
    checkOutLimit() {
      let day = addDays(this.checkIn, 1);
      const last = addDays(this.checkIn, this.cfg.maxNights);
      while (day < last && day < this.max && !this.unavailable(toIso(day))) day = addDays(day, 1);
      return day < this.max ? day : this.max;
    }

    /** Plazas libres en todas las noches elegidas (la noche más llena manda). */
    rangeFree() {
      let free = this.cfg.capacity;
      for (let day = this.checkIn; day < this.checkOut; day = addDays(day, 1)) {
        free = Math.min(free, this.free(toIso(day)));
      }
      return free;
    }

    /** Texto de las plazas de un día: "4 plazas", "¡Quedan 2!", "Completo", "Cerrado". */
    spotsText(iso, short = false) {
      if (this.blocked.has(iso)) return short ? "–" : this.t.closed;
      const free = this.free(iso);
      if (short) return String(free);
      if (free === 0) return this.t.full;
      if (free === 1) return this.t.spots_last;
      if (free === 2) return this.t.spots_few.replace("{n}", free);
      return this.t.spots_many.replace("{n}", free);
    }

    canCheckOut(date) {
      if (!this.checkIn || date <= this.checkIn) return false;
      const nights = daysBetween(this.checkIn, date);
      return nights >= this.cfg.minNights && nights <= this.cfg.maxNights && date <= this.checkOutLimit();
    }

    choosingCheckOut() {
      return Boolean(this.checkIn && !this.checkOut);
    }

    select(date) {
      if (this.choosingCheckOut() && this.canCheckOut(date)) {
        this.checkOut = date;
      } else if (this.canCheckIn(date)) {
        this.checkIn = date;
        this.checkOut = null;
      }
      this.hover = null;
      this.sync();
      this.paint();
    }

    clear() {
      this.checkIn = null;
      this.checkOut = null;
      this.sync();
      this.paint();
    }

    sync() {
      this.inInput.value = this.checkIn ? toIso(this.checkIn) : "";
      this.outInput.value = this.checkOut ? toIso(this.checkOut) : "";
    }

    /* ---------- Interfaz ---------- */
    build() {
      const t = this.t;
      const monday = Date.UTC(2024, 0, 1); // el 1 de enero de 2024 fue lunes
      const weekdays = Array.from({ length: 7 }, (_, i) =>
        `<span>${this.fmtWeekday.format(new Date(monday + i * DAY))}</span>`).join("");

      this.root.innerHTML = `
        <div class="mcal__toolbar">
          <button type="button" class="mcal__nav" data-nav="-1" aria-label="${t.prev}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
          <p class="mcal__title" aria-live="polite"></p>
          <button type="button" class="mcal__nav" data-nav="1" aria-label="${t.next}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
          </button>
        </div>
        <div class="mcal__table">
          <div class="mcal__weekdays">${weekdays}</div>
          <div class="mcal__grid"></div>
        </div>
        <p class="mcal__legend">${escape(t.spots_legend.replace("{capacity}", this.cfg.capacity))}</p>
        <div class="mcal__list"></div>
        <div class="mcal__bar">
          <div class="mcal__boxes">
            <div class="mcal__box" data-box="in"><span>${t.check_in}</span><strong></strong></div>
            <div class="mcal__box" data-box="out"><span>${t.check_out}</span><strong></strong></div>
          </div>
          <div class="mcal__info">
            <p class="mcal__status" aria-live="polite"></p>
            <p class="mcal__people"></p>
            <button type="button" class="mcal__clear">${t.clear}</button>
          </div>
          <button type="button" class="mcal__join">${this.root.dataset.joinLabel}</button>
        </div>`;

      this.title = this.root.querySelector(".mcal__title");
      this.grid = this.root.querySelector(".mcal__grid");
      this.list = this.root.querySelector(".mcal__list");
      this.prevBtn = this.root.querySelector('[data-nav="-1"]');
      this.nextBtn = this.root.querySelector('[data-nav="1"]');
      this.boxIn = this.root.querySelector('[data-box="in"] strong');
      this.boxOut = this.root.querySelector('[data-box="out"] strong');
      this.status = this.root.querySelector(".mcal__status");
      this.people = this.root.querySelector(".mcal__people");
      this.clearBtn = this.root.querySelector(".mcal__clear");
      this.joinBtn = this.root.querySelector(".mcal__join");

      this.prevBtn.addEventListener("click", () => this.shift(-1));
      this.nextBtn.addEventListener("click", () => this.shift(1));
      this.clearBtn.addEventListener("click", () => this.clear());
      this.joinBtn.addEventListener("click", () => this.openDialog());

      this.grid.addEventListener("click", (e) => {
        const day = e.target.closest("[data-date]");
        if (day && !day.disabled) this.select(parse(day.dataset.date));
      });
      this.grid.addEventListener("mouseover", (e) => {
        const day = e.target.closest("[data-date]");
        if (!day || !this.choosingCheckOut()) return;
        this.hover = parse(day.dataset.date);
        this.paint();
      });
      this.grid.addEventListener("mouseleave", () => {
        this.hover = null;
        this.paint();
      });
    }

    shift(step) {
      this.view = new Date(Date.UTC(this.view.getUTCFullYear(), this.view.getUTCMonth() + step, 1));
      this.render();
    }

    render() {
      const year = this.view.getUTCFullYear();
      const month = this.view.getUTCMonth();
      const daysInMonth = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
      const offset = (this.view.getUTCDay() + 6) % 7; // la semana empieza en lunes
      const trailing = (7 - ((offset + daysInMonth) % 7)) % 7;

      let cells = '<span class="mcal__blank"></span>'.repeat(offset);
      let listItems = "";
      for (let d = 1; d <= daysInMonth; d++) {
        const date = new Date(Date.UTC(year, month, d));
        const iso = toIso(date);
        const events = this.cfg.events[iso] || [];
        const eventsHtml = events.map(([time, name]) =>
          `<span class="mcal__event"><b>${escape(time)}</b> ${escape(name)}</span>`).join("");
        const weekend = date.getUTCDay() === 0 || date.getUTCDay() === 6;
        const classes = ["mcal__day"];
        if (weekend) classes.push("is-weekend");
        if (events.length) classes.push("has-events");
        // Plazas: solo en los días que aún se pueden reservar
        let spots = "";
        if (date >= this.min && date < this.max) {
          const free = this.free(iso);
          if (this.blocked.has(iso)) classes.push("is-closed");
          else if (free === 0) classes.push("is-full");
          else if (free <= 2) classes.push("is-few");
          spots = `<span class="mcal__spots"><span class="mcal__spots-long">${escape(this.spotsText(iso))}</span>` +
                  `<span class="mcal__spots-short">${escape(this.spotsText(iso, true))}</span></span>`;
        }
        cells += `
          <button type="button" class="${classes.join(" ")}" data-date="${iso}">
            <span class="mcal__num">${d}</span>
            <span class="mcal__events">${eventsHtml}</span>
            ${spots}
          </button>`;
        events.forEach(([time, name]) => {
          listItems += `<li${date < this.today ? ' class="is-past"' : ""}>
            <span>${escape(capitalize(this.fmtLong.format(date)))}</span> <b>${escape(time)}</b> ${escape(name)}</li>`;
        });
      }
      cells += '<span class="mcal__blank"></span>'.repeat(trailing);

      this.grid.innerHTML = cells;
      this.title.textContent = capitalize(this.fmtMonth.format(this.view));
      this.list.innerHTML = listItems
        ? `<p class="mcal__list-title">${escape(this.t.events_of.replace("{month}", this.fmtMonthName.format(this.view)))}</p><ul>${listItems}</ul>`
        : `<p class="mcal__list-title">${escape(this.t.no_events)}</p>`;

      // Flechas: no ir antes del mes actual ni después del último mes reservable
      this.prevBtn.disabled = this.view <= monthStart(this.min);
      this.nextBtn.disabled = monthStart(this.max) <= this.view;

      this.paint();
    }

    /** Actualiza solo los estados de los días (sin reconstruir el mes). */
    paint() {
      const choosingOut = this.choosingCheckOut();
      const rangeEnd = this.checkOut || (choosingOut && this.hover && this.canCheckOut(this.hover) ? this.hover : null);
      const limit = choosingOut ? this.checkOutLimit() : null;

      this.grid.querySelectorAll("[data-date]").forEach((btn) => {
        const date = parse(btn.dataset.date);
        const iso = btn.dataset.date;
        const isStart = Boolean(this.checkIn) && iso === toIso(this.checkIn);
        const isEnd = Boolean(rangeEnd) && iso === toIso(rangeEnd);
        const inRange = Boolean(this.checkIn && rangeEnd) && date > this.checkIn && date < rangeEnd;
        const validOut = choosingOut && this.canCheckOut(date);
        const available = this.canCheckIn(date) || validOut;
        const blocked = this.unavailable(iso) && date >= this.min;

        btn.disabled = !available && !isStart;
        btn.classList.toggle("is-past", date < this.min);
        btn.classList.toggle("is-today", iso === toIso(this.today));
        btn.classList.toggle("is-start", isStart);
        btn.classList.toggle("is-end", isEnd);
        btn.classList.toggle("is-range", inRange);
        btn.classList.toggle("is-blocked", blocked && !validOut);
        btn.classList.toggle("is-dim", Boolean(choosingOut && date > limit));
        btn.setAttribute("aria-pressed", String(isStart || isEnd));

        const events = (this.cfg.events[iso] || []).map(([time, name]) => `${time} ${name}`).join(", ");
        const spots = date >= this.min && date < this.max ? this.spotsText(iso) : "";
        btn.setAttribute("aria-label", [capitalize(this.fmtLong.format(date)), events, spots,
          available ? "" : this.t.unavailable].filter(Boolean).join(". "));
      });

      // Barra de abajo: llegada / salida, noches, personas y botón
      const complete = Boolean(this.checkIn && this.checkOut);
      this.boxIn.textContent = this.checkIn ? this.fmtShort.format(this.checkIn) : this.t.add_date;
      this.boxOut.textContent = this.checkOut ? this.fmtShort.format(this.checkOut) : this.t.add_date;

      if (complete) {
        const n = daysBetween(this.checkIn, this.checkOut);
        const capacity = this.cfg.capacity;
        const free = this.rangeFree();
        const text = free === capacity ? this.t.range_empty : free === 1 ? this.t.range_one : this.t.range_many;
        this.status.textContent = `${n} ${n === 1 ? this.t.night : this.t.nights}`;
        this.people.textContent = text.replace("{n}", free).replace("{capacity}", capacity)
          .replace("{taken}", capacity - free);
        this.people.classList.toggle("is-few", free <= 2);
      } else {
        this.status.textContent = choosingOut ? this.t.pick_check_out : this.t.pick_check_in;
        this.people.textContent = "";
      }
      this.root.classList.toggle("is-complete", complete);
      this.clearBtn.hidden = !this.checkIn;
      this.joinBtn.disabled = !complete;
    }

    /* ---------- Formulario (dialog) ---------- */
    datesText() {
      const n = daysBetween(this.checkIn, this.checkOut);
      return `${this.fmtShort.format(this.checkIn)} → ${this.fmtShort.format(this.checkOut)} · ${n} ${n === 1 ? this.t.night : this.t.nights}`;
    }

    openDialog() {
      if (!this.checkIn || !this.checkOut) return;
      this.dialog.querySelector("[data-dialog-dates]").textContent = this.datesText();
      if (!this.dialog.open) this.dialog.showModal();
      const first = this.dialog.querySelector(".field__input");
      if (first && !this.dialog.querySelector(".has-error")) first.focus();
    }

    initDialog() {
      const close = () => this.dialog.close();
      this.dialog.querySelector("[data-dialog-close]").addEventListener("click", close);
      this.dialog.querySelector("[data-dialog-change]").addEventListener("click", () => {
        close();
        this.root.closest("section").scrollIntoView({ behavior: "smooth", block: "start" });
      });
      // Clic fuera del formulario: cerrar
      this.dialog.addEventListener("click", (e) => {
        if (e.target === this.dialog) close();
      });

      // El servidor ha devuelto errores: abrir otra vez con lo que estaba escrito
      if (this.dialog.hasAttribute("data-open")) {
        if (this.checkIn && this.checkOut) {
          this.openDialog();
        } else {
          // Las fechas ya no valen: que elija otras en el calendario
          this.root.closest("section").scrollIntoView({ block: "start" });
          this.status.textContent = this.dialog.querySelector(".join__alert")?.textContent || this.status.textContent;
        }
      }
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-month-calendar]").forEach((el) => new MonthCalendar(el));
  });
})();
