# Finance Tracker

Sistema de gestão financeira pessoal: registre receitas e despesas, acompanhe
saldo por categoria e visualize a evolução mensal em gráficos.

## Stack

- **Back-end:** Python + Flask, Flask-SQLAlchemy, Flask-Login
- **Banco de dados:** SQLite (padrão) — pronto para trocar por PostgreSQL via `DATABASE_URL`
- **Front-end:** HTML + CSS (identidade visual "livro-caixa") + Chart.js
- **Testes:** pytest

## Funcionalidades

- Cadastro e login de usuários (senha com hash, sessão via Flask-Login)
- Categorias padrão criadas automaticamente no primeiro acesso
- CRUD completo de transações (criar, listar, editar, excluir)
- Filtros por tipo, categoria e período
- Dashboard com saldo do mês, saldo acumulado e últimos lançamentos
- Gráfico de pizza (gastos por categoria) e gráfico de barras (evolução dos últimos 6 meses)

## Como rodar localmente

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar a aplicação
python run.py
```

Acesse **http://localhost:5000** — o banco SQLite (`finance.db`) é criado
automaticamente na primeira execução.

## Rodando os testes

```bash
pytest
```

## Estrutura do projeto

```
finance-tracker/
├── app/
│   ├── __init__.py        # Application factory
│   ├── models.py          # Usuario, Categoria, Transacao, Meta
│   ├── routes/
│   │   ├── auth.py        # Registro, login, logout
│   │   ├── transacoes.py  # CRUD de transações + filtros
│   │   └── dashboard.py   # Resumo financeiro + endpoints JSON p/ gráficos
│   ├── templates/
│   └── static/
│       ├── css/style.css
│       └── js/charts.js
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

## Variáveis de ambiente

| Variável        | Descrição                              | Padrão                    |
|-----------------|------------------------------------------|---------------------------|
| `SECRET_KEY`    | Chave secreta do Flask (sessões/cookies) | chave de desenvolvimento  |
| `DATABASE_URL`  | URI de conexão com o banco               | SQLite local               |

Em produção, defina `SECRET_KEY` com um valor aleatório forte e `DATABASE_URL`
apontando para um banco PostgreSQL (ex: fornecido pelo Render ou Railway).

## Próximos passos sugeridos

- Metas de economia (modelo `Meta` já existe, falta a interface)
- Transações recorrentes (assinaturas, contas fixas)
- Exportação de relatórios em PDF/Excel
- Deploy em Render/Railway com PostgreSQL
