/**
 * Calendario del mes del inicio. Sin librerías.
 *
 * Arriba hay dos pestañas para que cada persona diga qué quiere (si cfg.staysEnabled):
 * - "Un plan": cada día muestra sus planes (hora, nombre y plazas que quedan). Al tocar un día,
 *   la barra de abajo enseña el plan y "Reservar plaza" abre el formulario.
 * - "Unos días": primer clic llegada, segundo clic último día (el mismo si es solo uno). Se reserva
 *   y se cobra POR DÍA, ambos incluidos. Cada día muestra las plazas libres del grupo.
 *
 * El precio NO se enseña en el calendario: aparece dentro del formulario, con el total según
 * las personas, cuando la persona ya ha elegido (y con "no pagas nada ahora").
 * En "Unos días", el formulario enseña los planes que caen dentro de la estancia para apuntarse.
 *
 * Lee data-config (lo prepara main_controller.booking_calendar):
 *   { min, max, staysEnabled, blocked: ["AAAA-MM-DD"], capacity, stayPrice,
 *     taken: {"AAAA-MM-DD": personas}, minDays, maxDays, lang, labels,
 *     events: {"AAAA-MM-DD": [{id, time, name, price, capacity, free}, …]} }
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
  const escape = (text) => String(text).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

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
      this.typeInput = this.dialog.querySelector("[data-booking-type]");
      this.eventInput = this.dialog.querySelector("[data-event-id]");
      this.inInput = this.dialog.querySelector("[data-check-in]");
      this.outInput = this.dialog.querySelector("[data-check-out]");
      this.peopleSelect = this.dialog.querySelector('select[name="people"]');
      this.hover = null;
      this.current = null; // lo que se está reservando en el formulario: {type, event?, days?}
      this.stayBox = this.dialog.querySelector("[data-stay-events]");
      this.stayList = this.dialog.querySelector("[data-stay-events-list]");
      // Planes que ya estaban marcados si el formulario vuelve con errores
      this.preselected = new Set(JSON.parse(this.stayBox.dataset.selected || "[]"));

      const tz = { timeZone: "UTC" };
      const lang = this.cfg.lang;
      this.fmtMonth = new Intl.DateTimeFormat(lang, { month: "long", year: "numeric", ...tz });
      this.fmtMonthName = new Intl.DateTimeFormat(lang, { month: "long", ...tz });
      this.fmtShort = new Intl.DateTimeFormat(lang, { day: "numeric", month: "short", year: "numeric", ...tz });
      this.fmtDay = new Intl.DateTimeFormat(lang, { weekday: "short", day: "numeric", month: "short", ...tz });
      this.fmtLong = new Intl.DateTimeFormat(lang, { weekday: "long", day: "numeric", month: "long", ...tz });
      this.fmtWeekday = new Intl.DateTimeFormat(lang, { weekday: "short", ...tz });
      this.fmtPrice = new Intl.NumberFormat(lang, { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

      // Pestaña inicial y, si el formulario vuelve con errores, lo que ya estaba elegido
      this.mode = this.cfg.staysEnabled && this.typeInput.value === "stay" ? "stays" : "events";
      this.selected = null; // "Un plan": día elegido
      this.checkIn = null;  // "Unos días": primer y último día (incluidos)
      this.checkOut = null;
      if (this.mode === "events") {
        const found = this.findEvent(this.eventInput.value);
        if (found) this.selected = found.date;
      } else {
        const savedIn = this.inInput.value;
        const savedOut = this.outInput.value;
        this.checkIn = isIso(savedIn) && this.canCheckIn(parse(savedIn)) ? parse(savedIn) : null;
        this.checkOut = this.checkIn && isIso(savedOut) && this.canCheckOut(parse(savedOut)) ? parse(savedOut) : null;
      }
      this.view = monthStart(this.selected || this.checkIn || this.firstEventDate() || this.min);

      this.build();
      this.render();
      this.initDialog();
    }

    get eventsMode() {
      return this.mode === "events";
    }

    plural(n, one, many) {
      return `${n} ${n === 1 ? one : many}`;
    }

    /* ---------- Planes ---------- */
    eventsOn(iso) {
      return this.cfg.events[iso] || [];
    }

    findEvent(id) {
      if (!id) return null;
      const iso = id.split("_")[0];
      const event = this.eventsOn(iso).find((e) => e.id === id);
      return event ? { event, date: parse(iso) } : null;
    }

    /** Primer día con plan desde hoy (para abrir el calendario en el mes que toca). */
    firstEventDate() {
      const first = Object.keys(this.cfg.events).sort().find((iso) => parse(iso) >= this.min);
      return first ? parse(first) : null;
    }

    /** "Quedan 3 de 12 plazas", "¡Solo quedan 2 plazas!", "¡Última plaza!", "Completo". */
    leftText(event) {
      if (event.free === 0) return this.t.full;
      if (event.free === 1) return this.t.left_last;
      if (event.free <= 3) return this.t.left_few.replace("{n}", event.free);
      return this.t.left_many.replace("{n}", event.free).replace("{capacity}", event.capacity);
    }

    /** Versión corta para el cuadro del día: "quedan 3" o "Completo". */
    shortText(event) {
      return event.free === 0 ? this.t.full : this.t.free_short.replace("{n}", event.free);
    }

    /* ---------- Días de estancia ---------- */
    /** Plazas libres ese día. */
    free(iso) {
      return Math.max(this.cfg.capacity - (this.cfg.taken[iso] || 0), 0);
    }

    /** Día que no se puede reservar: casa cerrada o grupo completo. */
    unavailable(iso) {
      return this.blocked.has(iso) || this.free(iso) === 0;
    }

    canCheckIn(date) {
      return date >= this.min && date < this.max && !this.unavailable(toIso(date));
    }

    /** Último día posible: el día antes del primer día sin plaza (o el máximo de días). */
    checkOutLimit() {
      let day = this.checkIn;
      const last = addDays(this.checkIn, this.cfg.maxDays - 1);
      while (day < last && addDays(day, 1) < this.max && !this.unavailable(toIso(addDays(day, 1)))) {
        day = addDays(day, 1);
      }
      return day;
    }

    canCheckOut(date) {
      if (!this.checkIn || date < this.checkIn) return false;
      const days = daysBetween(this.checkIn, date) + 1;
      return days >= this.cfg.minDays && days <= this.cfg.maxDays && date <= this.checkOutLimit();
    }

    stayDays() {
      return daysBetween(this.checkIn, this.checkOut) + 1;
    }

    /** Plazas libres en todos los días elegidos (el día más lleno manda). */
    rangeFree() {
      let free = this.cfg.capacity;
      for (let day = this.checkIn; day <= this.checkOut; day = addDays(day, 1)) {
        free = Math.min(free, this.free(toIso(day)));
      }
      return free;
    }

    /** Plazas de un día: "4 plazas", "¡Quedan 2!", "¡Última plaza!", "Completo", "Cerrado". */
    spotsText(iso, short = false) {
      if (this.blocked.has(iso)) return short ? "–" : this.t.closed;
      const free = this.free(iso);
      if (short) return String(free);
      if (free === 0) return this.t.full;
      if (free === 1) return this.t.spots_last;
      if (free === 2) return this.t.spots_few.replace("{n}", free);
      return this.t.spots_many.replace("{n}", free);
    }

    choosingCheckOut() {
      return !this.eventsMode && Boolean(this.checkIn && !this.checkOut);
    }

    /* ---------- Selección ---------- */
    canSelect(date) {
      if (date < this.min || date >= this.max) return false;
      if (this.eventsMode) return this.eventsOn(toIso(date)).length > 0;
      return this.canCheckIn(date) || (this.choosingCheckOut() && this.canCheckOut(date));
    }

    select(date) {
      if (this.eventsMode) {
        this.selected = date;
      } else if (this.choosingCheckOut() && this.canCheckOut(date)) {
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
      this.selected = null;
      this.checkIn = null;
      this.checkOut = null;
      this.sync();
      this.paint();
    }

    setMode(mode) {
      if (mode === this.mode) return;
      this.mode = mode;
      // Primero la barra nueva y luego pintar (si no, se pintaría la barra de la otra pestaña)
      this.selected = null;
      this.checkIn = null;
      this.checkOut = null;
      this.hover = null;
      this.sync();
      this.buildBar();
      this.render();
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
      const modeButton = (mode, title, hint) => `
        <button type="button" class="mcal__mode" data-mode="${mode}">
          <strong>${escape(title)}</strong>
          <span>${escape(hint.replace("{capacity}", this.cfg.capacity))}</span>
        </button>`;

      this.root.innerHTML = `
        ${this.cfg.staysEnabled ? `
          <div class="mcal__modes" role="group">
            ${modeButton("events", t.mode_events, t.mode_events_hint)}
            ${modeButton("stays", t.mode_stays, t.mode_stays_hint)}
          </div>` : ""}
        <div class="mcal__toolbar">
          <button type="button" class="mcal__nav" data-nav="-1" aria-label="${escape(t.prev)}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
          </button>
          <p class="mcal__title" aria-live="polite"></p>
          <button type="button" class="mcal__nav" data-nav="1" aria-label="${escape(t.next)}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
          </button>
        </div>
        <div class="mcal__table">
          <div class="mcal__weekdays">${weekdays}</div>
          <div class="mcal__grid"></div>
        </div>
        <p class="mcal__legend"></p>
        <div class="mcal__list"></div>
        <div class="mcal__bar"></div>`;

      this.title = this.root.querySelector(".mcal__title");
      this.grid = this.root.querySelector(".mcal__grid");
      this.legend = this.root.querySelector(".mcal__legend");
      this.list = this.root.querySelector(".mcal__list");
      this.bar = this.root.querySelector(".mcal__bar");
      this.prevBtn = this.root.querySelector('[data-nav="-1"]');
      this.nextBtn = this.root.querySelector('[data-nav="1"]');
      this.prevBtn.addEventListener("click", () => this.shift(-1));
      this.nextBtn.addEventListener("click", () => this.shift(1));
      this.root.querySelectorAll("[data-mode]").forEach((btn) =>
        btn.addEventListener("click", () => this.setMode(btn.dataset.mode)));

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
      // En el móvil, la lista de planes del mes también sirve para elegir día
      this.list.addEventListener("click", (e) => {
        const item = e.target.closest("[data-pick]");
        if (!item || item.disabled) return;
        this.select(parse(item.dataset.pick));
        this.bar.scrollIntoView({ behavior: "smooth", block: "nearest" });
      });
      // Botones de la barra ("Reservar plaza", "Borrar fechas")
      this.bar.addEventListener("click", (e) => {
        const book = e.target.closest("[data-book]");
        if (book && !book.disabled) this.openDialog(book.dataset.book);
        if (e.target.closest("[data-clear]")) this.clear();
      });

      this.buildBar();
    }

    /** La barra de abajo cambia según la pestaña. */
    buildBar() {
      const t = this.t;
      this.root.querySelectorAll("[data-mode]").forEach((btn) =>
        btn.setAttribute("aria-pressed", String(btn.dataset.mode === this.mode)));
      this.root.classList.toggle("is-events", this.eventsMode);
      this.root.classList.toggle("is-stays", !this.eventsMode);

      this.bar.innerHTML = this.eventsMode
        ? `<div class="mcal__plans" aria-live="polite"></div>`
        : `<div class="mcal__boxes">
             <div class="mcal__box" data-box="in"><span>${escape(t.check_in)}</span><strong></strong></div>
             <div class="mcal__box" data-box="out"><span>${escape(t.check_out)}</span><strong></strong></div>
           </div>
           <div class="mcal__info">
             <p class="mcal__status" aria-live="polite"></p>
             <p class="mcal__people"></p>
             <button type="button" class="mcal__clear" data-clear>${escape(t.clear)}</button>
           </div>
           <button type="button" class="mcal__join" data-book="stay">${escape(t.book)}</button>`;
    }

    shift(step) {
      this.view = new Date(Date.UTC(this.view.getUTCFullYear(), this.view.getUTCMonth() + step, 1));
      this.render();
    }

    /** Contenido de un cuadro del día (sin precios). */
    dayContent(date, iso, classes) {
      const bookable = date >= this.min && date < this.max;
      const events = this.eventsOn(iso);

      if (this.eventsMode) {
        if (bookable && events.length) {
          if (events.every((e) => e.free === 0)) classes.push("is-full");
          else if (events.some((e) => e.free > 0 && e.free <= 3)) classes.push("is-few");
        }
        return events.map((e) => `
          <span class="mcal__event${e.free === 0 ? " is-full" : e.free <= 3 ? " is-few" : ""}">
            <b>${escape(e.time)}</b> ${escape(e.name)}
            ${bookable ? `<small>${escape(this.shortText(e))}</small>` : ""}
          </span>`).join("");
      }

      // "Unos días": los planes se ven como referencia y cada día dice las plazas del grupo
      let html = events.map((e) => `<span class="mcal__event"><b>${escape(e.time)}</b> ${escape(e.name)}</span>`).join("");
      if (bookable) {
        const free = this.free(iso);
        if (this.blocked.has(iso)) classes.push("is-closed");
        else if (free === 0) classes.push("is-full");
        else if (free <= 2) classes.push("is-few");
        html += `<span class="mcal__spots"><span class="mcal__spots-long">${escape(this.spotsText(iso))}</span>` +
                `<span class="mcal__spots-short">${escape(this.spotsText(iso, true))}</span></span>`;
      }
      return html;
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
        const events = this.eventsOn(iso);
        const weekend = date.getUTCDay() === 0 || date.getUTCDay() === 6;
        const classes = ["mcal__day"];
        if (weekend) classes.push("is-weekend");
        if (events.length) classes.push("has-events");
        const content = this.dayContent(date, iso, classes);
        cells += `
          <button type="button" class="${classes.join(" ")}" data-date="${iso}">
            <span class="mcal__num">${d}</span>
            <span class="mcal__events">${content}</span>
          </button>`;

        // Lista de planes del mes (se ve en el móvil). Sin precios.
        const past = date < this.today;
        events.forEach((e) => {
          const extra = this.eventsMode && !past ? ` · ${escape(this.leftText(e))}` : "";
          listItems += `
            <li class="${past ? "is-past" : ""}">
              <button type="button" data-pick="${iso}"${past || !this.eventsMode ? " disabled" : ""}>
                <span>${escape(capitalize(this.fmtLong.format(date)))}</span>
                <b>${escape(e.time)}</b> ${escape(e.name)}${extra}
              </button>
            </li>`;
        });
      }
      cells += '<span class="mcal__blank"></span>'.repeat(trailing);

      this.grid.innerHTML = cells;
      this.title.textContent = capitalize(this.fmtMonth.format(this.view));
      this.legend.textContent = this.eventsMode
        ? this.t.events_legend
        : this.t.spots_legend.replace("{capacity}", this.cfg.capacity);
      this.list.innerHTML = listItems
        ? `<p class="mcal__list-title">${escape(this.t.events_of.replace("{month}", this.fmtMonthName.format(this.view)))}</p><ul>${listItems}</ul>`
        : `<p class="mcal__list-title">${escape(this.t.no_events)}</p>`;

      // Flechas: no ir antes del mes actual ni después del último mes reservable
      this.prevBtn.disabled = this.view <= monthStart(this.min);
      this.nextBtn.disabled = monthStart(this.max) <= this.view;

      this.paint();
    }

    /** Actualiza solo los estados de los días y la barra (sin reconstruir el mes). */
    paint() {
      const choosingOut = this.choosingCheckOut();
      const rangeEnd = this.checkOut || (choosingOut && this.hover && this.canCheckOut(this.hover) ? this.hover : null);
      const limit = choosingOut ? this.checkOutLimit() : null;

      this.grid.querySelectorAll("[data-date]").forEach((btn) => {
        const date = parse(btn.dataset.date);
        const iso = btn.dataset.date;
        const isStart = this.eventsMode
          ? Boolean(this.selected) && iso === toIso(this.selected)
          : Boolean(this.checkIn) && iso === toIso(this.checkIn);
        const isEnd = Boolean(rangeEnd) && iso === toIso(rangeEnd);
        const inRange = Boolean(this.checkIn && rangeEnd) && date > this.checkIn && date < rangeEnd;

        btn.disabled = !this.canSelect(date) && !isStart;
        btn.classList.toggle("is-past", date < this.min);
        btn.classList.toggle("is-today", iso === toIso(this.today));
        btn.classList.toggle("is-start", isStart);
        btn.classList.toggle("is-end", isEnd);
        btn.classList.toggle("is-range", inRange);
        btn.classList.toggle("is-blocked", !this.eventsMode && date >= this.min && this.unavailable(iso));
        btn.classList.toggle("is-dim", Boolean(choosingOut && (date > limit || date < this.checkIn)));
        btn.setAttribute("aria-pressed", String(isStart || isEnd));

        const bookable = date >= this.min && date < this.max;
        const parts = [capitalize(this.fmtLong.format(date))];
        this.eventsOn(iso).forEach((e) => {
          parts.push(`${e.time} ${e.name}` + (this.eventsMode && bookable ? `, ${this.leftText(e)}` : ""));
        });
        if (!this.eventsMode && bookable) parts.push(this.spotsText(iso));
        btn.setAttribute("aria-label", parts.join(". "));
      });

      if (this.eventsMode) this.paintPlans();
      else this.paintStayBar(choosingOut);
    }

    /** Barra de "Un plan": el plan del día elegido con su botón (sin precio). */
    paintPlans() {
      const plans = this.bar.querySelector(".mcal__plans");
      if (!this.selected) {
        plans.innerHTML = `<p class="mcal__hint">${escape(this.t.pick_event)}</p>`;
        return;
      }
      plans.innerHTML = this.eventsOn(toIso(this.selected)).map((e) => `
        <div class="mcal__plan${e.free === 0 ? " is-full" : e.free <= 3 ? " is-few" : ""}">
          <div class="mcal__plan-info">
            <strong class="mcal__plan-name">${escape(e.name)}</strong>
            <span class="mcal__plan-when">${escape(capitalize(this.fmtDay.format(this.selected)))} · ${escape(e.time)}</span>
            <span class="mcal__plan-left">${escape(this.leftText(e))}</span>
          </div>
          <button type="button" class="mcal__join" data-book="${escape(e.id)}"${e.free === 0 ? " disabled" : ""}>
            ${escape(e.free === 0 ? this.t.full : this.t.book)}
          </button>
        </div>`).join("");
    }

    /** Barra de "Unos días": llegada / último día, días y plazas (sin precio). */
    paintStayBar(choosingOut) {
      const t = this.t;
      const complete = Boolean(this.checkIn && this.checkOut);
      const status = this.bar.querySelector(".mcal__status");
      const people = this.bar.querySelector(".mcal__people");
      this.bar.querySelector('[data-box="in"] strong').textContent =
        this.checkIn ? this.fmtShort.format(this.checkIn) : t.add_date;
      this.bar.querySelector('[data-box="out"] strong').textContent =
        this.checkOut ? this.fmtShort.format(this.checkOut) : t.add_date;

      if (complete) {
        const capacity = this.cfg.capacity;
        const free = this.rangeFree();
        const text = free === capacity ? t.range_empty : free === 1 ? t.range_one : t.range_many;
        status.textContent = this.plural(this.stayDays(), t.day, t.days);
        people.textContent = text.replace("{n}", free).replace("{capacity}", capacity).replace("{taken}", capacity - free);
        people.classList.toggle("is-few", free <= 2);
      } else {
        status.textContent = choosingOut ? t.pick_check_out : t.pick_check_in;
        people.textContent = "";
      }
      this.root.classList.toggle("is-complete", complete);
      this.bar.querySelector("[data-clear]").hidden = !this.checkIn;
      this.bar.querySelector("[data-book]").disabled = !complete;
    }

    /* ---------- Formulario (dialog) ---------- */
    /** Solo se puede elegir hasta las plazas que quedan. */
    limitPeople(free) {
      if (!this.peopleSelect) return;
      const options = [...this.peopleSelect.options].filter((o) => o.value);
      options.forEach((o) => { o.disabled = Number(o.value) > free; });
      const max = Math.max(1, ...options.filter((o) => !o.disabled).map((o) => Number(o.value)));
      if (!this.peopleSelect.value) this.peopleSelect.value = "1";
      if (Number(this.peopleSelect.value) > free) this.peopleSelect.value = String(max);
    }

    /** Precio con el total según las personas: "25 € por persona · 2 × 25 € = 50 € en total". */
    updatePrice() {
      const box = this.dialog.querySelector("[data-dialog-price]");
      if (!box || !this.current) return;
      const t = this.t;
      const people = Number(this.peopleSelect && this.peopleSelect.value) || 1;
      if (this.current.type === "event") {
        const price = this.current.event.price;
        box.textContent = `${this.fmtPrice.format(price)} ${t.per_person}` +
          (people > 1 ? ` · ${t.price_total.replace("{amount}", this.fmtPrice.format(price * people))}` : "");
      } else {
        const price = this.cfg.stayPrice;
        const days = this.current.days;
        const plans = this.checkedStayEvents().reduce((sum, e) => sum + e.price, 0);
        box.textContent = `${this.fmtPrice.format(price)} ${t.per_person_day} · ` +
          t.price_total.replace("{amount}", this.fmtPrice.format((price * days + plans) * people));
      }
    }

    /* ---------- Planes dentro de una estancia ---------- */
    /** Planes desde la llegada hasta el último día (ambos incluidos). */
    stayEvents() {
      const items = [];
      for (let day = this.checkIn; day <= this.checkOut; day = addDays(day, 1)) {
        if (day < this.min) continue;
        this.eventsOn(toIso(day)).forEach((event) => items.push({ event, date: day }));
      }
      return items;
    }

    checkedStayEvents() {
      return [...this.stayList.querySelectorAll("input:checked")]
        .map((input) => this.findEvent(input.value)).filter(Boolean).map((found) => found.event);
    }

    renderStayEvents() {
      const isStay = this.current && this.current.type === "stay";
      const items = isStay ? this.stayEvents() : [];
      this.stayBox.hidden = items.length === 0;
      this.stayList.innerHTML = items.map(({ event, date }) => `
        <label class="plan-option">
          <input type="checkbox" name="stay_events" value="${escape(event.id)}"
                 ${this.preselected.has(event.id) ? "checked" : ""}${event.free === 0 ? " disabled" : ""}>
          <span class="plan-option__box">
            <strong>${escape(event.name)}</strong>
            <span>${escape(capitalize(this.fmtDay.format(date)))} · ${escape(event.time)} ·
              <em>${escape(this.leftText(event))}</em></span>
          </span>
          <span class="plan-option__price">+${escape(this.fmtPrice.format(event.price))}</span>
        </label>`).join("");
      this.preselected.clear();
      this.stayList.querySelectorAll("input").forEach((input) =>
        input.addEventListener("change", () => this.updatePrice()));
      this.refreshStayEvents();
    }

    /** Un plan sin sitio para tantas personas no se puede marcar. */
    refreshStayEvents() {
      const people = Number(this.peopleSelect && this.peopleSelect.value) || 1;
      this.stayList.querySelectorAll("input").forEach((input) => {
        const found = this.findEvent(input.value);
        const noRoom = !found || found.event.free < people;
        input.disabled = noRoom;
        if (noRoom) input.checked = false;
        input.closest(".plan-option").classList.toggle("is-disabled", noRoom);
      });
    }

    openDialog(what) {
      const t = this.t;
      let summary;
      if (what !== "stay") {
        const found = this.findEvent(what);
        if (!found || found.event.free === 0) return;
        const { event, date } = found;
        this.typeInput.value = "event";
        this.eventInput.value = event.id;
        this.current = { type: "event", event };
        summary = `${event.name} · ${capitalize(this.fmtDay.format(date))} · ${event.time}`;
        this.dialog.querySelector("[data-dialog-label]").textContent = t.your_plan;
        this.dialog.querySelector("[data-dialog-change]").textContent = t.change_plan;
        this.limitPeople(event.free);
      } else {
        if (!this.checkIn || !this.checkOut) return;
        const days = this.stayDays();
        this.typeInput.value = "stay";
        this.eventInput.value = "";
        this.current = { type: "stay", days };
        summary = (days === 1 ? this.fmtShort.format(this.checkIn)
          : `${this.fmtShort.format(this.checkIn)} → ${this.fmtShort.format(this.checkOut)}`) +
          ` · ${this.plural(days, t.day, t.days)}`;
        this.dialog.querySelector("[data-dialog-label]").textContent = t.your_dates;
        this.dialog.querySelector("[data-dialog-change]").textContent = t.change_dates;
        this.limitPeople(this.rangeFree());
      }
      this.dialog.querySelector("[data-dialog-dates]").textContent = summary;
      this.renderStayEvents();
      this.updatePrice();
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
      if (this.peopleSelect) {
        this.peopleSelect.addEventListener("change", () => {
          this.refreshStayEvents();
          this.updatePrice();
        });
      }

      // El servidor ha devuelto errores: abrir otra vez con lo que estaba escrito
      if (this.dialog.hasAttribute("data-open")) {
        const found = this.eventsMode ? this.findEvent(this.eventInput.value) : null;
        const canReopen = this.eventsMode ? Boolean(found && found.event.free > 0) : Boolean(this.checkIn && this.checkOut);
        if (canReopen) {
          this.openDialog(this.eventsMode ? this.eventInput.value : "stay");
        } else {
          // Lo elegido ya no vale (p. ej. se ha llenado): que elija otra cosa en el calendario
          this.root.closest("section").scrollIntoView({ block: "start" });
          const alert = this.dialog.querySelector(".join__alert");
          if (alert) {
            const note = document.createElement("p");
            note.className = "mcal__alert";
            note.textContent = alert.textContent;
            this.root.prepend(note);
          }
        }
      }
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-month-calendar]").forEach((el) => new MonthCalendar(el));
  });
})();
