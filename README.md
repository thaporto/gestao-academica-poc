7# Gestão Acadêmica: Prova de Conceito (PoC)

Projeto Integrador 4 do curso de Tecnologia em Análise e Desenvolvimento de Sistemas do **Senac EAD**: *Desenvolvimento de Sistema Orientado a Dispositivos Móveis e Baseados na Web*.

Professor: **Anderson Clayton**

## Equipe

| Integrante | Usuário no GitHub |
|---|---|
| Igor Borges Krobath | `@Igor.Krobath` |
| Jamile Marques Lima | `@JamileM` |
| Julia Assis Miguel | `@Assisjulia` |
| Renan Rodrigues de Almeida | `@usuario` |
| Thais Aparecida Porto | [@ThaisPorto026](https://github.com/ThaisPorto026) |
| Yasmin Oliveira Dantas | `@usuario` |

## Sobre o projeto

Na 1ª entrega, o grupo propôs um **sistema web responsivo de gestão acadêmica** para instituições de ensino de pequeno e médio porte, que hoje controlam alunos, turmas, docentes e fornecedores em planilhas espalhadas.

Nesta 2ª entrega foi desenvolvida uma **prova de conceito (PoC)** com uma única jornada, escolhida por concentrar o principal valor e os maiores riscos técnicos do sistema:

> **A Secretária Acadêmica (persona Mariana) entra no sistema, cadastra um aluno com validação de CPF, matricula esse aluno em uma turma e recebe o número de matrícula gerado automaticamente.**

### O que a PoC comprova

| Regra de negócio | Como foi implementada |
|---|---|
| Só usuários autenticados acessam os dados | Login com senha criptografada (hash) e sessão; a API responde 401 sem login |
| O CPF precisa ser válido | Cálculo dos dígitos verificadores no navegador e no servidor |
| O mesmo aluno não pode ser cadastrado duas vezes | CPF único no banco e verificação antes de gravar (resposta 409) |
| O aluno não pode ser matriculado duas vezes na mesma turma | Restrição `UNIQUE (aluno_id, turma_id)` e verificação na API |
| A turma não pode passar do número de vagas | Contagem das matrículas ativas antes de gravar |
| Cada matrícula recebe um número único | Formato `AAAA` + sequencial de 4 dígitos (ex.: `20260001`), gerado dentro de uma transação |

### Fora do escopo da PoC

Cadastro de docentes, fornecedores, pessoas jurídicas (CNPJ), perfis de Administração e Financeiro, edição e exclusão de registros e relatórios. Esses itens ficam para as próximas etapas e seguem o mesmo padrão de API e telas.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Frontend | HTML5, CSS3 (layout responsivo com Grid/Flexbox) e JavaScript puro (`fetch`) |
| Backend | Python 3 + Flask (API REST em JSON) |
| Banco de dados | SQLite (arquivo local, sem instalação de servidor) |
| Testes | `unittest` (biblioteca padrão do Python) |
| Versionamento | Git e GitHub |

## Arquitetura

![Arquitetura](docs/arquitetura.png)

O navegador carrega as páginas HTML, que chamam a API em `/api/...` usando `fetch`. A API aplica as regras de negócio e grava no banco SQLite. O mesmo servidor Flask entrega as páginas e a API, então basta um comando para rodar tudo.

## Modelo de dados

![Diagrama entidade-relacionamento](docs/der.png)

O script completo está em [`backend/schema.sql`](backend/schema.sql) e os dados de exemplo (3 cursos e 4 turmas) em [`backend/seed.sql`](backend/seed.sql).

## Estrutura de pastas

```
gestao-academica-poc/
├── backend/
│   ├── app.py              # API REST e servidor das páginas
│   ├── database.py         # conexão e criação do banco
│   ├── validacoes.py       # regras: CPF, e-mail, datas
│   ├── schema.sql          # criação das tabelas
│   ├── seed.sql            # dados de exemplo
│   ├── requirements.txt    # dependências Python
│   └── tests/
│       └── test_api.py     # 13 testes automatizados
├── frontend/
│   ├── index.html          # login
│   ├── matricula.html      # nova matrícula (jornada principal)
│   ├── alunos.html         # cadastro e busca de alunos
│   ├── matriculas.html     # consulta das matrículas
│   ├── css/style.css
│   └── js/
│       ├── comum.js        # chamada à API, máscaras e validação de CPF
│       ├── alunos.js
│       └── matricula.js
└── docs/
    ├── arquitetura.png
    ├── der.png
    └── telas/              # capturas de tela
```

## Como executar

### 1. Pré-requisitos

- [Python 3.10 ou superior](https://www.python.org/downloads/). No Windows, marque a opção **"Add Python to PATH"** durante a instalação.
- [Git](https://git-scm.com/downloads)

### 2. Baixar o projeto

```bash
git clone https://github.com/ThaisPorto026/gestao-academica-poc.git
cd gestao-academica-poc/backend
```

### 3. Criar o ambiente virtual e instalar as dependências

Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Subir o servidor

```bash
python app.py
```

Na primeira execução, o banco `gestao_academica.db` é criado automaticamente com os cursos, as turmas e o usuário de demonstração.

### 5. Acessar

Abra **http://localhost:5000** no navegador e entre com:

| E-mail | Senha |
|---|---|
| `secretaria@escola.edu.br` | `senac123` |

Para testar no celular, conecte-o à mesma rede Wi-Fi, troque a última linha do `app.py` por `app.run(debug=True, host="0.0.0.0", port=5000)` e acesse `http://IP-DO-COMPUTADOR:5000`.

### Recriar o banco do zero

```bash
python database.py
```

### Rodar os testes automatizados

```bash
python -m unittest discover -s tests -v
```

Resultado esperado: `Ran 13 tests ... OK`.

## Roteiro de demonstração

1. Entrar com o usuário de demonstração.
2. Em **Alunos**, cadastrar um aluno com o CPF `123.456.789-00` e ver o aviso de CPF inválido.
3. Corrigir para `529.982.247-25` e concluir o cadastro.
4. Tentar cadastrar outra pessoa com o mesmo CPF e ver o bloqueio de duplicidade.
5. Clicar em **Matricular agora**, escolher a turma `INF-2026-M` e confirmar: o número `20260001` é exibido.
6. Tentar matricular o mesmo aluno na mesma turma e ver o bloqueio.
7. A turma `ENF-2026-N` tem só 2 vagas: depois de 2 matrículas, ela aparece como **Sem vagas**.
8. Em **Matrículas**, consultar a lista.

CPFs válidos para testes: `529.982.247-25`, `111.444.777-35`, `390.533.447-05`.

## API

Todas as rotas, exceto o login, exigem sessão ativa.

| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| POST | `/api/login` | Entra no sistema (`email`, `senha`) | 200, 401 |
| POST | `/api/logout` | Encerra a sessão | 200 |
| GET | `/api/sessao` | Dados do usuário logado | 200, 401 |
| GET | `/api/turmas` | Turmas com curso, vagas ocupadas e disponíveis | 200 |
| GET | `/api/alunos?busca=` | Lista alunos, com busca por nome ou CPF | 200 |
| POST | `/api/alunos` | Cadastra aluno (`nome`, `cpf`, `data_nascimento`, `email`, `telefone`) | 201, 400, 409 |
| GET | `/api/matriculas` | Lista as matrículas | 200 |
| POST | `/api/matriculas` | Matricula (`aluno_id`, `turma_id`) e devolve o número gerado | 201, 400, 404, 409 |

Exemplo de resposta de `POST /api/matriculas`:

```json
{
  "numero": "20260001",
  "aluno": "Ana Paula Souza",
  "cpf": "529.982.247-25",
  "curso": "Técnico em Informática",
  "turma": "INF-2026-M",
  "periodo": "Manhã"
}
```

## Telas

| Login | Nova matrícula | Matrícula concluída |
|---|---|---|
| ![Login](docs/telas/01_login.png) | ![Seleção](docs/telas/06_matricula_selecao.png) | ![Concluída](docs/telas/07_matricula_concluida.png) |

| CPF inválido | CPF duplicado | Versão celular |
|---|---|---|
| ![CPF inválido](docs/telas/02_cpf_invalido.png) | ![Duplicado](docs/telas/04_cpf_duplicado.png) | ![Celular](docs/telas/11_mobile.png) |

## Vídeo de demonstração

Link: *(inserir o link do YouTube não listado ou o caminho do MP4 no repositório)*
