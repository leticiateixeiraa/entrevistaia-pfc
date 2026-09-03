"""
test(auth-backend): adiciona testes de registro e login

Rode com: pytest
Requer um banco de teste configurado via variável de ambiente DATABASE_URL
(ou ajuste para usar SQLite em memória, se preferir isolar de vez os testes).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login():
    payload = {
        "email": "teste_leticia@example.com",
        "password": "senha-forte-123",
        "name": "Usuária de Teste",
    }

    register_response = client.post("/auth/register", json=payload)
    assert register_response.status_code == 201
    assert register_response.json()["email"] == payload["email"]

    login_response = client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_login_com_senha_errada_falha():
    response = client.post(
        "/auth/login",
        json={"email": "teste_leticia@example.com", "password": "senha-errada"},
    )
    assert response.status_code == 401
