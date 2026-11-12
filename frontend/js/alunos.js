/* =====================================================================
   Tela de alunos: cadastro (com validação) e consulta
   ===================================================================== */

const formAluno = document.getElementById("form-aluno");
const aviso = document.getElementById("aviso");
const tabelaAlunos = document.getElementById("tabela-alunos");
const semAlunos = document.getElementById("sem-alunos");
const campoBusca = document.getElementById("busca");
const campos = ["nome", "cpf", "data_nascimento", "email", "telefone"];

function mostrarAviso(texto, tipo) {
  aviso.textContent = texto;
  aviso.className = `aviso ${tipo}`;
}

function limparErros() {
  aviso.textContent = "";
  aviso.className = "aviso";
  campos.forEach((c) => {
    document.getElementById(c).removeAttribute("aria-invalid");
    document.getElementById(`erro-${c}`).textContent = "";
  });
}

function mostrarErroCampo(campo, mensagem) {
  const input = document.getElementById(campo);
  if (!input) return;
  input.setAttribute("aria-invalid", "true");
  document.getElementById(`erro-${campo}`).textContent = mensagem;
}

/** Confere os campos no navegador antes de enviar. Devolve true se estiver tudo certo. */
function validarFormulario() {
  let ok = true;
  const v = (c) => document.getElementById(c).value.trim();

  if (v("nome").length < 3) { mostrarErroCampo("nome", "Informe o nome completo do aluno."); ok = false; }
  if (!cpfValido(v("cpf"))) { mostrarErroCampo("cpf", "CPF inválido. Confira os 11 dígitos."); ok = false; }

  const nascimento = v("data_nascimento");
  if (!nascimento || nascimento >= new Date().toISOString().slice(0, 10)) {
    mostrarErroCampo("data_nascimento", "Informe uma data de nascimento anterior a hoje.");
    ok = false;
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v("email"))) {
    mostrarErroCampo("email", "Informe um e-mail válido, como nome@dominio.com.");
    ok = false;
  }
  const telefone = v("telefone").replace(/\D/g, "");
  if (telefone && ![10, 11].includes(telefone.length)) {
    mostrarErroCampo("telefone", "O telefone precisa ter DDD + número (10 ou 11 dígitos).");
    ok = false;
  }
  return ok;
}

async function carregarAlunos() {
  const busca = campoBusca.value.trim();
  const alunos = await api(`/api/alunos${busca ? `?busca=${encodeURIComponent(busca)}` : ""}`);

  tabelaAlunos.innerHTML = alunos.map((a) => `
    <tr>
      <td data-rotulo="Nome">${escapar(a.nome)}</td>
      <td class="cpf" data-rotulo="CPF">${escapar(a.cpf)}</td>
      <td class="data" data-rotulo="Nascimento">${escapar(dataBR(a.data_nascimento))}</td>
      <td data-rotulo="E-mail">${escapar(a.email)}</td>
      <td class="acao"><a href="matricula.html?aluno=${encodeURIComponent(a.id)}">Matricular</a></td>
    </tr>`).join("");
  semAlunos.hidden = alunos.length > 0;
}

formAluno.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  limparErros();
  if (!validarFormulario()) {
    mostrarAviso("Corrija os campos destacados.", "erro");
    return;
  }

  const botao = formAluno.querySelector("button[type=submit]");
  botao.disabled = true;
  try {
    const dados = Object.fromEntries(campos.map((c) => [c, document.getElementById(c).value.trim()]));
    const aluno = await api("/api/alunos", { method: "POST", body: JSON.stringify(dados) });
    formAluno.reset();
    mostrarAviso(`Aluno ${aluno.nome} cadastrado com sucesso.`, "sucesso");
    await carregarAlunos();
  } catch (erro) {
    Object.entries(erro.campos || {}).forEach(([campo, msg]) => mostrarErroCampo(campo, msg));
    mostrarAviso(erro.message, "erro");
  } finally {
    botao.disabled = false;
  }
});

document.getElementById("cpf").addEventListener("input", (e) => (e.target.value = mascaraCPF(e.target.value)));
document.getElementById("telefone").addEventListener("input", (e) => (e.target.value = mascaraTelefone(e.target.value)));

let temporizador;
campoBusca.addEventListener("input", () => {
  clearTimeout(temporizador);
  temporizador = setTimeout(() => carregarAlunos().catch((e) => mostrarAviso(e.message, "erro")), 250);
});

(async () => {
  try {
    await iniciarPaginaInterna();
    await carregarAlunos();
  } catch (erro) {
    mostrarAviso(erro.message, "erro");
  }
})();
