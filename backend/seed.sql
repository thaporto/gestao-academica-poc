-- =====================================================================
-- Carga inicial de dados para demonstração da PoC.
-- O usuário de acesso é criado pelo database.py, porque a senha
-- precisa ser gravada com hash.
-- =====================================================================

INSERT INTO cursos (nome, carga_horaria) VALUES
    ('Técnico em Informática', 1200),
    ('Técnico em Administração', 1000),
    ('Técnico em Enfermagem', 1800);

INSERT INTO turmas (curso_id, codigo, periodo, ano, vagas) VALUES
    (1, 'INF-2026-M', 'Manhã', 2026, 30),
    (1, 'INF-2026-N', 'Noite', 2026, 30),
    (2, 'ADM-2026-T', 'Tarde', 2026, 25),
    (3, 'ENF-2026-N', 'Noite', 2026, 2);   -- poucas vagas, para demonstrar o bloqueio de turma lotada
