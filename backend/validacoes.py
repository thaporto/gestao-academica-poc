"""
Regras de validação usadas pela API.

Ficam separadas das rotas para poderem ser testadas de forma isolada
(ver tests/test_api.py).
"""

import re
from datetime import date, datetime

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def cpf_valido(cpf):
    """
    Valida um CPF pelos dígitos verificadores.
    Aceita o CPF com ou sem máscara (000.000.000-00).
    """
    cpf = somente_digitos(cpf)

    # precisa ter 11 dígitos e não pode ser uma sequência repetida (ex.: 111.111.111-11)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for posicao in (9, 10):
        soma = sum(int(cpf[i]) * ((posicao + 1) - i) for i in range(posicao))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[posicao]):
            return False
    return True


def formatar_cpf(cpf):
    cpf = somente_digitos(cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf


def validar_aluno(dados):
    """
    Recebe o JSON enviado pelo formulário e devolve um dicionário
    {campo: mensagem} com os erros encontrados (vazio se estiver tudo certo).
    """
    erros = {}

    nome = (dados.get("nome") or "").strip()
    if len(nome) < 3:
        erros["nome"] = "Informe o nome completo do aluno."

    if not cpf_valido(dados.get("cpf")):
        erros["cpf"] = "CPF inválido. Confira os 11 dígitos."

    nascimento = (dados.get("data_nascimento") or "").strip()
    try:
        data = datetime.strptime(nascimento, "%Y-%m-%d").date()
        if data >= date.today():
            erros["data_nascimento"] = "A data de nascimento precisa ser anterior a hoje."
    except ValueError:
        erros["data_nascimento"] = "Informe a data de nascimento."

    email = (dados.get("email") or "").strip()
    if not EMAIL_REGEX.match(email):
        erros["email"] = "Informe um e-mail válido, como nome@dominio.com."

    telefone = somente_digitos(dados.get("telefone"))
    if telefone and len(telefone) not in (10, 11):
        erros["telefone"] = "O telefone precisa ter DDD + número (10 ou 11 dígitos)."

    return erros
