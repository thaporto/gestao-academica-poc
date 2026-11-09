"""
Gestão Acadêmica - Prova de Conceito (PoC)
Jornada: "Secretária Acadêmica cadastra um aluno e o matricula em uma turma"

Backend em Flask que:
  1. expõe uma API REST em /api/...
  2. serve as páginas do frontend (pasta ../frontend)

Para executar:  python app.py   ->  http://localhost:5000
"""

import os
import sqlite3
from datetime import date
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash

from database import get_connection, init_db
from validacoes import formatar_cpf, somente_digitos, validar_aluno

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

app = Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config["JSON_AS_ASCII"] = False


# ---------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------

def erro(mensagem, status, campos=None):
    corpo = {"erro": mensagem}
    if campos:
        corpo["campos"] = campos
    return jsonify(corpo), status


def login_obrigatorio(rota):
    """Bloqueia o acesso às rotas da API para quem não fez login."""
    @wraps(rota)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return erro("Sessão expirada. Entre novamente.", 401)
        return rota(*args, **kwargs)
    return verificar


def aluno_para_json(linha):
    aluno = dict(linha)
    aluno["cpf"] = formatar_cpf(aluno["cpf"])
    return aluno


# ---------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------

@app.post("/api/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip().lower()
    senha = dados.get("senha") or ""

    with get_connection() as conn:
        usuario = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()

    if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
        return erro("E-mail ou senha incorretos.", 401)

    session.clear()
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["perfil"] = usuario["perfil"]
    return jsonify({"nome": usuario["nome"], "perfil": usuario["perfil"]})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})


@app.get("/api/sessao")
@login_obrigatorio
def sessao_atual():
    return jsonify({"nome": session["usuario_nome"], "perfil": session["perfil"]})


# ---------------------------------------------------------------------
# Turmas
# ---------------------------------------------------------------------

@app.get("/api/turmas")
@login_obrigatorio
def listar_turmas():
    with get_connection() as conn:
        linhas = conn.execute(
            """
            SELECT t.id, t.codigo, t.periodo, t.ano, t.vagas,
                   c.nome AS curso,
                   COUNT(m.id) AS ocupadas
              FROM turmas t
              JOIN cursos c ON c.id = t.curso_id
              LEFT JOIN matriculas m ON m.turma_id = t.id AND m.status = 'ATIVA'
             GROUP BY t.id
             ORDER BY c.nome, t.codigo
            """
        ).fetchall()

    turmas = []
    for linha in linhas:
        turma = dict(linha)
        turma["disponiveis"] = turma["vagas"] - turma["ocupadas"]
        turmas.append(turma)
    return jsonify(turmas)


# ---------------------------------------------------------------------
# Alunos
# ---------------------------------------------------------------------

@app.get("/api/alunos")
@login_obrigatorio
def listar_alunos():
    busca = (request.args.get("busca") or "").strip()
    sql = "SELECT * FROM alunos"
    parametros = []
    if busca:
        sql += " WHERE nome LIKE ? OR cpf LIKE ?"
        parametros = [f"%{busca}%", f"%{somente_digitos(busca) or busca}%"]
    sql += " ORDER BY nome"

    with get_connection() as conn:
        linhas = conn.execute(sql, parametros).fetchall()
    return jsonify([aluno_para_json(l) for l in linhas])


@app.post("/api/alunos")
@login_obrigatorio
def cadastrar_aluno():
    dados = request.get_json(silent=True) or {}
    erros = validar_aluno(dados)
    if erros:
        return erro("Corrija os campos destacados.", 400, erros)

    cpf = somente_digitos(dados["cpf"])
    with get_connection() as conn:
        existente = conn.execute("SELECT nome FROM alunos WHERE cpf = ?", (cpf,)).fetchone()
        if existente:
            return erro(
                f"Este CPF já está cadastrado para {existente['nome']}.",
                409,
                {"cpf": "CPF já cadastrado."},
            )

        cursor = conn.execute(
            """INSERT INTO alunos (nome, cpf, data_nascimento, email, telefone)
               VALUES (?, ?, ?, ?, ?)""",
            (
                dados["nome"].strip(),
                cpf,
                dados["data_nascimento"],
                dados["email"].strip().lower(),
                somente_digitos(dados.get("telefone")) or None,
            ),
        )
        aluno = conn.execute("SELECT * FROM alunos WHERE id = ?", (cursor.lastrowid,)).fetchone()

    return jsonify(aluno_para_json(aluno)), 201


# ---------------------------------------------------------------------
# Matrículas
# ---------------------------------------------------------------------

def gerar_numero_matricula(conn, ano):
    """Número no formato AAAA + sequencial de 4 dígitos (ex.: 20260001)."""
    ultimo = conn.execute(
        "SELECT MAX(numero) FROM matriculas WHERE numero LIKE ?", (f"{ano}%",)
    ).fetchone()[0]
    sequencial = int(ultimo[4:]) + 1 if ultimo else 1
    return f"{ano}{sequencial:04d}"


@app.get("/api/matriculas")
@login_obrigatorio
def listar_matriculas():
    with get_connection() as conn:
        linhas = conn.execute(
            """
            SELECT m.id, m.numero, m.data_matricula, m.status,
                   a.nome AS aluno, a.cpf,
                   t.codigo AS turma, t.periodo,
                   c.nome AS curso
              FROM matriculas m
              JOIN alunos a ON a.id = m.aluno_id
              JOIN turmas t ON t.id = m.turma_id
              JOIN cursos c ON c.id = t.curso_id
             ORDER BY m.numero DESC
            """
        ).fetchall()
    return jsonify([aluno_para_json(l) for l in linhas])


@app.post("/api/matriculas")
@login_obrigatorio
def matricular():
    dados = request.get_json(silent=True) or {}
    aluno_id = dados.get("aluno_id")
    turma_id = dados.get("turma_id")
    if not aluno_id or not turma_id:
        return erro("Selecione o aluno e a turma.", 400)

    conn = get_connection()
    conn.isolation_level = None              # controle manual da transação
    try:
        # BEGIN IMMEDIATE reserva o banco para escrita: evita que duas
        # matrículas simultâneas recebam o mesmo número ou estourem as vagas.
        conn.execute("BEGIN IMMEDIATE")

        aluno = conn.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,)).fetchone()
        turma = conn.execute(
            """SELECT t.*, c.nome AS curso FROM turmas t
               JOIN cursos c ON c.id = t.curso_id WHERE t.id = ?""",
            (turma_id,),
        ).fetchone()
        if aluno is None or turma is None:
            conn.execute("ROLLBACK")
            return erro("Aluno ou turma não encontrados.", 404)

        ja_matriculado = conn.execute(
            "SELECT numero FROM matriculas WHERE aluno_id = ? AND turma_id = ?",
            (aluno_id, turma_id),
        ).fetchone()
        if ja_matriculado:
            conn.execute("ROLLBACK")
            return erro(
                f"{aluno['nome']} já está matriculado(a) nesta turma "
                f"(matrícula {ja_matriculado['numero']}).",
                409,
            )

        ocupadas = conn.execute(
            "SELECT COUNT(*) FROM matriculas WHERE turma_id = ? AND status = 'ATIVA'",
            (turma_id,),
        ).fetchone()[0]
        if ocupadas >= turma["vagas"]:
            conn.execute("ROLLBACK")
            return erro(f"A turma {turma['codigo']} não tem vagas disponíveis.", 409)

        numero = gerar_numero_matricula(conn, date.today().year)
        conn.execute(
            "INSERT INTO matriculas (numero, aluno_id, turma_id) VALUES (?, ?, ?)",
            (numero, aluno_id, turma_id),
        )
        conn.execute("COMMIT")
    except sqlite3.Error:
        conn.execute("ROLLBACK")
        return erro("Não foi possível concluir a matrícula. Tente novamente.", 500)
    finally:
        conn.close()

    return jsonify({
        "numero": numero,
        "aluno": aluno["nome"],
        "cpf": formatar_cpf(aluno["cpf"]),
        "curso": turma["curso"],
        "turma": turma["codigo"],
        "periodo": turma["periodo"],
    }), 201


# ---------------------------------------------------------------------
# Frontend (páginas HTML, CSS e JS)
# ---------------------------------------------------------------------

@app.get("/")
def pagina_inicial():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:arquivo>")
def arquivos_frontend(arquivo):
    return send_from_directory(FRONTEND_DIR, arquivo)


if __name__ == "__main__":
    if init_db():
        print("Banco de dados criado com os dados de exemplo.")
    print("Sistema disponível em http://localhost:5000")
    app.run(debug=True, port=5000)
