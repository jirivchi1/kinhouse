/* Interacciones de la página: tema claro/oscuro, pestañas y newsletter. */
(function () {
  "use strict";

  /* ---------- Modo claro / oscuro ---------- */
  function initTheme() {
    const root = document.documentElement;
    const media = window.matchMedia("(prefers-color-scheme: dark)");

    const saved = () => {
      try { return localStorage.getItem("theme"); } catch { return null; }
    };

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.addEventListener("click", () => {
        const next = root.dataset.theme === "dark" ? "light" : "dark";
        root.dataset.theme = next;
        try { localStorage.setItem("theme", next); } catch { /* sin almacenamiento */ }
      });
    });

    // Si el usuario no ha elegido, sigue los cambios del sistema
    media.addEventListener("change", (e) => {
      if (!saved()) root.dataset.theme = e.matches ? "dark" : "light";
    });
  }

  /* ---------- Pestañas ("Cómo trabajamos" y semanas de eventos) ---------- */
  function initTabs() {
    // Cada grupo de pestañas (role="tablist") funciona por separado
    document.querySelectorAll('[role="tablist"]').forEach((list) => {
      const tabs = list.querySelectorAll("[data-tab]");
      tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
          tabs.forEach((t) => {
            const active = t === tab;
            t.classList.toggle("is-active", active);
            t.setAttribute("aria-selected", String(active));
            const panel = document.getElementById(t.getAttribute("aria-controls"));
            panel.hidden = !active;
            panel.classList.toggle("is-active", active);
          });
        });
      });
    });
  }

  /* ---------- Newsletter (POST /subscribe) ---------- */
  function initNewsletter() {
    const form = document.querySelector("[data-newsletter]");
    if (!form) return;
    const msg = form.querySelector("[data-newsletter-msg]");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.classList.remove("is-error");
      msg.textContent = "…";
      try {
        const res = await fetch(form.action, { method: "POST", body: new FormData(form) });
        const data = await res.json();
        msg.textContent = data.message;
        msg.classList.toggle("is-error", !data.ok);
        if (data.ok) form.reset();
      } catch {
        msg.textContent = form.dataset.error;
        msg.classList.add("is-error");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initTabs();
    initNewsletter();
  });
})();
