/* =====================================================================
   Funções compartilhadas por todas as páginas
   ===================================================================== */

/**
 * Chama a API do backend e devolve o JSON.
 * Se a sessão tiver expirado (401), volta para a tela de login.
 */
async function api(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    ...opcoes,
  });

  const dados = await resposta.json().catch(() => ({}));

  if (resposta.status === 401 && !caminho.endsWith("/login")) {
    window.location.href = "index.html";
    throw new Error("Sessão expirada");
  }
  if (!resposta.ok) {
    const erro = new Error(dados.erro || "Erro inesperado. Tente novamente.");
    erro.campos = dados.campos || {};
    throw erro;
  }
  return dados;
}

/** Valida o CPF no navegador (mesma regra do backend), para avisar antes de enviar. */
function cpfValido(cpf) {
  cpf = (cpf || "").replace(/\D/g, "");
  if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;

  for (const posicao of [9, 10]) {
    let soma = 0;
    for (let i = 0; i < posicao; i++) soma += Number(cpf[i]) * (posicao + 1 - i);
    let digito = (soma * 10) % 11;
    if (digito === 10) digito = 0;
    if (digito !== Number(cpf[posicao])) return false;
  }
  return true;
}

/** Aplica a máscara 000.000.000-00 enquanto o usuário digita. */
function mascaraCPF(valor) {
  const d = valor.replace(/\D/g, "").slice(0, 11);
  return d
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
}

/** Aplica a máscara (00) 00000-0000. */
function mascaraTelefone(valor) {
  const d = valor.replace(/\D/g, "").slice(0, 11);
  if (d.length <= 2) return d.length ? `(${d}` : "";
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

/** Converte AAAA-MM-DD em DD/MM/AAAA. */
function dataBR(valor) {
  if (!valor) return "";
  const [ano, mes, dia] = valor.slice(0, 10).split("-");
  return `${dia}/${mes}/${ano}`;
}

/** Evita que textos digitados pelo usuário virem HTML na página. */
function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

/** Verifica a sessão e preenche o nome do usuário no menu. Usado nas páginas internas. */
async function iniciarPaginaInterna() {
  const usuario = await api("/api/sessao");
  document.querySelectorAll(".nome-usuario").forEach((el) => (el.textContent = usuario.nome));

  document.getElementById("sair")?.addEventListener("click", async () => {
    await api("/api/logout", { method: "POST" });
    window.location.href = "index.html";
  });
  return usuario;
}
