/* =====================================================================
   Tela de nova matrícula: aluno -> turma -> confirmação
   ===================================================================== */

const aviso = document.getElementById("aviso");
const listaAlunos = document.getElementById("lista-alunos");
const semAlunos = document.getElementById("sem-alunos");
const areaTurmas = document.getElementById("turmas");
const resumo = document.getElementById("resumo");
const botaoConfirmar = document.getElementById("confirmar");
const campoBusca = document.getElementById("busca");

let alunos = [];
let turmas = [];
let alunoSelecionado = null;
let turmaSelecionada = null;

function mostrarErro(texto) {
  aviso.textContent = texto;
  aviso.className = "aviso erro";
}

function atualizarEtapas() {
  const etapa = !alunoSelecionado ? 1 : !turmaSelecionada ? 2 : 3;
  [1, 2, 3].forEach((n) => {
    const li = document.getElementById(`etapa-${n}`);
    li.className = n < etapa ? "feita" : n === etapa ? "ativa" : "";
  });
}

function desenharAlunos() {
  listaAlunos.innerHTML = alunos.map((a) => `
    <li>
      <button type="button" data-id="${escapar(String(a.id))}"
              aria-pressed="${alunoSelecionado && alunoSelecionado.id === a.id}">
        ${escapar(a.nome)}<small>CPF ${escapar(a.cpf)}</small>
      </button>
    </li>`).join("");
  semAlunos.hidden = alunos.length > 0;
}

function desenharTurmas() {
  areaTurmas.innerHTML = turmas.map((t) => {
    const lotada = t.disponiveis <= 0;
    return `
      <button type="button" class="turma" data-id="${escapar(String(t.id))}"
              aria-pressed="${!!turmaSelecionada && turmaSelecionada.id === t.id}" ${lotada ? "disabled" : ""}>
        <strong>${escapar(t.codigo)}</strong>
        <small>${escapar(t.curso)}</small>
        <small>${escapar(t.periodo)} · ${escapar(String(t.ano))}</small>
        <span class="vagas">${lotada ? "Sem vagas" : `${t.disponiveis} de ${t.vagas} vagas disponíveis`}</span>
      </button>`;
  }).join("");
}

function atualizarResumo() {
  if (alunoSelecionado && turmaSelecionada) {
    resumo.innerHTML = `Matricular <strong>${escapar(alunoSelecionado.nome)}</strong>
      (CPF ${escapar(alunoSelecionado.cpf)}) na turma <strong>${escapar(turmaSelecionada.codigo)}</strong>
      · ${escapar(turmaSelecionada.curso)} · ${escapar(turmaSelecionada.periodo)}.`;
  } else {
    resumo.textContent = "Selecione um aluno e uma turma para continuar.";
  }
  botaoConfirmar.disabled = !(alunoSelecionado && turmaSelecionada);
  atualizarEtapas();
}

async function carregarAlunos() {
  const busca = campoBusca.value.trim();
  alunos = await api(`/api/alunos${busca ? `?busca=${encodeURIComponent(busca)}` : ""}`);
  desenharAlunos();
}

async function carregarTurmas() {
  turmas = await api("/api/turmas");
  // se a turma escolhida lotou nesse meio tempo, desfaz a escolha
  if (turmaSelecionada) {
    turmaSelecionada = turmas.find((t) => t.id === turmaSelecionada.id && t.disponiveis > 0) || null;
  }
  desenharTurmas();
  atualizarResumo();
}

listaAlunos.addEventListener("click", (e) => {
  const botao = e.target.closest("button[data-id]");
  if (!botao) return;
  alunoSelecionado = alunos.find((a) => String(a.id) === botao.dataset.id) || null;
  desenharAlunos();
  atualizarResumo();
});

areaTurmas.addEventListener("click", (e) => {
  const botao = e.target.closest("button[data-id]");
  if (!botao || botao.disabled) return;
  turmaSelecionada = turmas.find((t) => String(t.id) === botao.dataset.id) || null;
  desenharTurmas();
  atualizarResumo();
});

let temporizador;
campoBusca.addEventListener("input", () => {
  clearTimeout(temporizador);
  temporizador = setTimeout(() => carregarAlunos().catch((err) => mostrarErro(err.message)), 250);
});

botaoConfirmar.addEventListener("click", async () => {
  aviso.textContent = "";
  aviso.className = "aviso erro";
  botaoConfirmar.disabled = true;
  try {
    const m = await api("/api/matriculas", {
      method: "POST",
      body: JSON.stringify({ aluno_id: alunoSelecionado.id, turma_id: turmaSelecionada.id }),
    });
    document.getElementById("r-numero").textContent = m.numero;
    document.getElementById("r-aluno").textContent = m.aluno;
    document.getElementById("r-cpf").textContent = m.cpf;
    document.getElementById("r-curso").textContent = m.curso;
    document.getElementById("r-turma").textContent = m.turma;
    document.getElementById("r-periodo").textContent = m.periodo;
    document.getElementById("fluxo").hidden = true;
    document.getElementById("resultado").hidden = false;
    document.querySelectorAll(".etapas li").forEach((li) => (li.className = "feita"));
  } catch (erro) {
    mostrarErro(erro.message);
    await carregarTurmas().catch(() => {});   // atualiza as vagas após uma recusa
  } finally {
    botaoConfirmar.disabled = !(alunoSelecionado && turmaSelecionada);
  }
});

document.getElementById("nova").addEventListener("click", async () => {
  alunoSelecionado = null;
  turmaSelecionada = null;
  campoBusca.value = "";
  document.getElementById("resultado").hidden = true;
  document.getElementById("fluxo").hidden = false;
  try {
    await Promise.all([carregarAlunos(), carregarTurmas()]);
  } catch (erro) {
    mostrarErro(erro.message);
  }
  atualizarResumo();
});

(async () => {
  try {
    await iniciarPaginaInterna();
    await Promise.all([carregarAlunos(), carregarTurmas()]);
    // vindo da tela de alunos (?aluno=ID), já deixa o aluno selecionado
    const id = new URLSearchParams(window.location.search).get("aluno");
    if (id) {
      alunoSelecionado = alunos.find((a) => String(a.id) === id) || null;
      desenharAlunos();
    }
    atualizarResumo();
  } catch (erro) {
    mostrarErro(erro.message);
  }
})();
