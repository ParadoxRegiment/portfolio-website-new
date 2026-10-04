// Light/dark toggle: applies the chosen daisyUI theme and remembers it.
// The inline script in base.html re-applies the saved theme on every page load.

const toggle = document.querySelector("[data-theme-toggle]");

if (toggle) {
  const { light, dark } = toggle.dataset;  // theme names come from data-light / data-dark
  const root = document.documentElement;

  // What's showing right now: a saved choice, or the OS preference.
  const current =
    root.dataset.theme ?? (matchMedia("(prefers-color-scheme: dark)").matches ? dark : light);
  toggle.checked = current === dark;

  toggle.addEventListener("change", () => {
    const theme = toggle.checked ? dark : light;
    root.dataset.theme = theme;  // sets <html data-theme="...">
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // storage blocked (e.g. some private modes): theme still applies for this page
    }
  });
}