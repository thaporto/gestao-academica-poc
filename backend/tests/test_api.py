"""
Testes automatizados da PoC.

Executar a partir da pasta backend:
    python -m unittest discover -s tests -v

Cada teste usa um banco temporário, então os dados reais não são afetados.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from validacoes import cpf_valido  # noqa: E402

CPF_VALIDO_1 = "529.982.247-25"
CPF_VALIDO_2 = "111.444.777-35"
CPF_VALIDO_3 = "390.533.447-05"


class TestValidacaoCPF(unittest.TestCase):
    def test_cpf_valido_com_e_sem_mascara(self):
        self.assertTrue(cpf_valido(CPF_VALIDO_1))
        self.assertTrue(cpf_valido("52998224725"))

    def test_cpf_com_digito_errado(self):
        self.assertFalse(cpf_valido("529.982.247-26"))

    def test_cpf_sequencia_repetida(self):
        self.assertFalse(cpf_valido("111.111.111-11"))

    def test_cpf_tamanho_errado(self):
        self.assertFalse(cpf_valido("123"))
        self.assertFalse(cpf_valido(""))


class TestJornadaMatricula(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DB_PATH"] = os.path.join(self.tmp.name, "teste.db")

        import database
        import app as app_module
        database.init_db(reset=True)

        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("DB_PATH", None)

    # ---------- auxiliares ----------
    def entrar(self):
        return self.client.post("/api/login", json={
            "email": "secretaria@escola.edu.br", "senha": "senac123"})

    def cadastrar(self, cpf=CPF_VALIDO_1, nome="Ana Souza"):
        return self.client.post("/api/alunos", json={
            "nome": nome, "cpf": cpf, "data_nascimento": "2005-03-10",
            "email": "ana@email.com", "telefone": "(11) 98888-7777"})

    def turma_id(self, codigo):
        turmas = self.client.get("/api/turmas").get_json()
        return next(t["id"] for t in turmas if t["codigo"] == codigo)

    # ---------- autenticação ----------
    def test_login_com_senha_errada(self):
        resp = self.client.post("/api/login", json={
            "email": "secretaria@escola.edu.br", "senha": "errada"})
        self.assertEqual(resp.status_code, 401)

    def test_api_bloqueada_sem_login(self):
        self.assertEqual(self.client.get("/api/alunos").status_code, 401)

    def test_login_correto(self):
        self.assertEqual(self.entrar().status_code, 200)

    # ---------- cadastro de aluno ----------
    def test_cadastro_aluno_valido(self):
        self.entrar()
        resp = self.cadastrar()
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["cpf"], CPF_VALIDO_1)

    def test_cadastro_bloqueia_cpf_invalido(self):
        self.entrar()
        resp = self.cadastrar(cpf="123.456.789-00")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("cpf", resp.get_json()["campos"])

    def test_cadastro_bloqueia_cpf_duplicado(self):
        self.entrar()
        self.cadastrar()
        resp = self.cadastrar(nome="Outra Pessoa")
        self.assertEqual(resp.status_code, 409)

    # ---------- matrícula ----------
    def test_matricula_gera_numero_sequencial(self):
        self.entrar()
        a1 = self.cadastrar(CPF_VALIDO_1).get_json()["id"]
        a2 = self.cadastrar(CPF_VALIDO_2, "Bruno Lima").get_json()["id"]
        turma = self.turma_id("INF-2026-M")

        r1 = self.client.post("/api/matriculas", json={"aluno_id": a1, "turma_id": turma})
        r2 = self.client.post("/api/matriculas", json={"aluno_id": a2, "turma_id": turma})
        self.assertEqual(r1.status_code, 201)
        n1, n2 = r1.get_json()["numero"], r2.get_json()["numero"]
        self.assertEqual(len(n1), 8)
        self.assertEqual(int(n2), int(n1) + 1)

    def test_matricula_duplicada_na_mesma_turma(self):
        self.entrar()
        aluno = self.cadastrar().get_json()["id"]
        turma = self.turma_id("INF-2026-M")
        self.client.post("/api/matriculas", json={"aluno_id": aluno, "turma_id": turma})
        resp = self.client.post("/api/matriculas", json={"aluno_id": aluno, "turma_id": turma})
        self.assertEqual(resp.status_code, 409)

    def test_matricula_em_turma_lotada(self):
        self.entrar()
        turma = self.turma_id("ENF-2026-N")          # turma com apenas 2 vagas
        for cpf, nome in [(CPF_VALIDO_1, "Ana Souza"), (CPF_VALIDO_2, "Bruno Lima")]:
            aluno = self.cadastrar(cpf, nome).get_json()["id"]
            self.client.post("/api/matriculas", json={"aluno_id": aluno, "turma_id": turma})

        terceiro = self.cadastrar(CPF_VALIDO_3, "Carla Dias").get_json()["id"]
        resp = self.client.post("/api/matriculas", json={"aluno_id": terceiro, "turma_id": turma})
        self.assertEqual(resp.status_code, 409)
        self.assertIn("vagas", resp.get_json()["erro"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
