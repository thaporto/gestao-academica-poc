-- =====================================================================
-- Gestão Acadêmica - PoC "Matrícula de Aluno"
-- Esquema do banco de dados (SQLite)
-- =====================================================================

PRAGMA foreign_keys = ON;

-- Usuários internos que acessam o sistema (Secretaria, Administração...)
CREATE TABLE IF NOT EXISTS usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    senha_hash  TEXT    NOT NULL,
    perfil      TEXT    NOT NULL CHECK (perfil IN ('ADMINISTRACAO', 'SECRETARIA', 'FINANCEIRO'))
);

-- Cursos oferecidos pela instituição
CREATE TABLE IF NOT EXISTS cursos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT    NOT NULL UNIQUE,
    carga_horaria  INTEGER NOT NULL CHECK (carga_horaria > 0)
);

-- Turmas de cada curso
CREATE TABLE IF NOT EXISTS turmas (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    curso_id  INTEGER NOT NULL REFERENCES cursos(id),
    codigo    TEXT    NOT NULL UNIQUE,
    periodo   TEXT    NOT NULL CHECK (periodo IN ('Manhã', 'Tarde', 'Noite')),
    ano       INTEGER NOT NULL,
    vagas     INTEGER NOT NULL CHECK (vagas > 0)
);

-- Alunos (pessoas físicas): o CPF é único para impedir cadastro duplicado
CREATE TABLE IF NOT EXISTS alunos (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    nome             TEXT    NOT NULL,
    cpf              TEXT    NOT NULL UNIQUE,      -- somente os 11 dígitos
    data_nascimento  TEXT    NOT NULL,             -- formato AAAA-MM-DD
    email            TEXT    NOT NULL,
    telefone         TEXT,
    criado_em        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Matrículas: vínculo entre aluno e turma, com número gerado pelo sistema
CREATE TABLE IF NOT EXISTS matriculas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero          TEXT    NOT NULL UNIQUE,       -- ex.: 20260001
    aluno_id        INTEGER NOT NULL REFERENCES alunos(id),
    turma_id        INTEGER NOT NULL REFERENCES turmas(id),
    data_matricula  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    status          TEXT    NOT NULL DEFAULT 'ATIVA' CHECK (status IN ('ATIVA', 'CANCELADA')),
    UNIQUE (aluno_id, turma_id)                    -- o aluno não pode ser matriculado duas vezes na mesma turma
);
