"""
Acesso ao banco de dados SQLite.

- get_connection(): abre uma conexão com chaves estrangeiras ativadas.
- init_db(): cria as tabelas (schema.sql), carrega os dados de exemplo
  (seed.sql) e cria o usuário da Secretaria Acadêmica.
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "gestao_academica.db")

# Usuário de demonstração (persona Mariana, Secretária Acadêmica)
USUARIO_DEMO = {
    "nome": "Mariana Oliveira",
    "email": "secretaria@escola.edu.br",
    "senha": "senac123",
    "perfil": "SECRETARIA",
}


def get_db_path():
    """Permite trocar o arquivo do banco pela variável de ambiente DB_PATH (usada nos testes)."""
    return os.environ.get("DB_PATH", DEFAULT_DB_PATH)


class Conexao(sqlite3.Connection):
    """
    Conexão que, ao sair do bloco "with", grava (commit) ou desfaz (rollback)
    e também FECHA a conexão. O sqlite3 padrão só faz o commit e deixa o
    arquivo aberto, o que no Windows impede apagar o banco (ex.: nos testes).
    """

    def __exit__(self, tipo, valor, traceback):
        try:
            return super().__exit__(tipo, valor, traceback)
        finally:
            self.close()


def get_connection():
    conn = sqlite3.connect(get_db_path(), factory=Conexao)
    conn.row_factory = sqlite3.Row          # permite acessar colunas pelo nome
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _run_sql_file(conn, filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        conn.executescript(f.read())


def init_db(reset=False):
    """Cria o banco se ele ainda não existir. Com reset=True, apaga e recria."""
    path = get_db_path()
    if reset and os.path.exists(path):
        os.remove(path)

    novo_banco = not os.path.exists(path)
    conn = get_connection()
    try:
        _run_sql_file(conn, "schema.sql")
        if novo_banco:
            _run_sql_file(conn, "seed.sql")
            conn.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
                (
                    USUARIO_DEMO["nome"],
                    USUARIO_DEMO["email"],
                    generate_password_hash(USUARIO_DEMO["senha"]),
                    USUARIO_DEMO["perfil"],
                ),
            )
            conn.commit()
    finally:
        conn.close()
    return novo_banco


if __name__ == "__main__":
    # python database.py  -> recria o banco do zero com os dados de exemplo
    init_db(reset=True)
    print(f"Banco recriado em {get_db_path()}")
    print(f"Login: {USUARIO_DEMO['email']}  |  Senha: {USUARIO_DEMO['senha']}")
