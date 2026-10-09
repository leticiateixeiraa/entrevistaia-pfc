"""
Fixtures dos testes de integração.

Cada teste monta o próprio cenário: o banco de teste (SQLite em memória,
configurado em tests/conftest.py) é apagado e recriado ANTES de cada teste,
então nenhum teste depende de dados deixados por outro nem da ordem de
execução.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import base

SENHA_PADRAO = "Entrevista#2026"


@pytest.fixture(autouse=True)
def banco_vazio():
    base.Base.metadata.drop_all(bind=base.engine)
    base.Base.metadata.create_all(bind=base.engine)
    yield


@pytest.fixture
def client():
    """Cliente HTTP que conversa com a API de verdade (rotas, validação,
    services e banco de teste), sem subir servidor nem abrir porta."""
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def db():
    """Sessão direta no banco de teste, para preparar ou conferir dados."""
    with base.SessionLocal() as sessao:
        yield sessao


@pytest.fixture
def cadastrar(client):
    """Devolve uma função que cadastra um usuário pela API."""

    def _cadastrar(email: str = "aluna@umc.br", senha: str = SENHA_PADRAO):
        resposta = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": senha,
                "name": "Aluna de Teste",
                "terms_accepted": True,
            },
        )
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _cadastrar


@pytest.fixture
def emails_enviados(monkeypatch):
    """Substitui o envio real de e-mail por uma lista em memória.

    Cada item é uma tupla (destinatário, token), o que permite ao teste
    "abrir o e-mail" e usar o link de redefinição sem depender de SMTP.
    """
    caixa_de_saida = []
    monkeypatch.setattr(
        "app.auth.router.enviar_email_redefinicao_senha",
        lambda email, token: caixa_de_saida.append((email, token)),
    )
    return caixa_de_saida
