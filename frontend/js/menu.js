/* Abre e fecha o menu lateral no celular (botão, fundo escuro, tecla Esc e links). */
(function () {
  const menu = document.getElementById("menu");
  const botao = document.getElementById("abrir-menu");
  const fundo = document.getElementById("fundo-menu");
  if (!menu || !botao || !fundo) return;

  function definir(aberto) {
    menu.classList.toggle("aberto", aberto);
    fundo.hidden = !aberto;
    botao.setAttribute("aria-expanded", String(aberto));
    botao.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
    document.body.style.overflow = aberto ? "hidden" : "";
  }

  botao.addEventListener("click", () => definir(!menu.classList.contains("aberto")));
  fundo.addEventListener("click", () => definir(false));
  menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => definir(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") definir(false); });
  window.matchMedia("(min-width: 861px)").addEventListener("change", (e) => { if (e.matches) definir(false); });
})();
