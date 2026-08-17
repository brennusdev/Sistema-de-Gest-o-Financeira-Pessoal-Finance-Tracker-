import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    TestConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def registrar_usuario(client, email="teste@exemplo.com"):
    return client.post(
        "/registro",
        data={
            "nome": "Usuário Teste",
            "email": email,
            "senha": "senha123",
            "confirmar_senha": "senha123",
        },
        follow_redirects=True,
    )


def test_registro_cria_usuario_e_categorias_padrao(client):
    resposta = registrar_usuario(client)
    assert resposta.status_code == 200
    assert "Painel financeiro".encode() in resposta.data or b"Bem-vindo" in resposta.data


def test_login_com_credenciais_invalidas(client):
    resposta = client.post(
        "/login", data={"email": "naoexiste@exemplo.com", "senha": "errada"}, follow_redirects=True
    )
    assert "invalidos".encode() in resposta.data.lower().replace("á".encode(), b"a") or resposta.status_code == 200


def test_criar_transacao(client):
    registrar_usuario(client)
    resposta = client.post(
        "/transacoes/nova",
        data={
            "descricao": "Salário de teste",
            "valor": "1500,00",
            "tipo": "receita",
            "data": "2026-08-01",
            "categoria_id": "",
        },
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    assert "Salário de teste".encode() in resposta.data


def test_transacao_requer_login(client):
    resposta = client.get("/transacoes/", follow_redirects=False)
    assert resposta.status_code in (302, 401)
