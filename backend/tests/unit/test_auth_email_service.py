"""
Testes unitários do envio do e-mail de redefinição de senha
(app/auth/email_service.py).

A dependência externa aqui é o servidor SMTP. Ele é substituído por um mock
(`unittest.mock.MagicMock`, o equivalente em Python ao Mockito): nenhum
e-mail de verdade é enviado e nenhuma conexão de rede é aberta.
"""
from email import message_from_string
from unittest.mock import MagicMock

import pytest

from app.auth import email_service
from app.auth.email_service import ErroEnvioEmail, enviar_email_redefinicao_senha

DESTINATARIO = "aluna@umc.br"
TOKEN = "token-de-teste-123"


@pytest.fixture
def smtp_falso(monkeypatch):
    """Troca a classe smtplib.SMTP por um mock e devolve os dois objetos:
    a classe falsa (para saber se alguém tentou conectar) e o servidor falso
    (para conferir o que foi pedido a ele)."""
    classe_smtp = MagicMock(name="smtplib.SMTP")
    servidor = classe_smtp.return_value.__enter__.return_value
    monkeypatch.setattr(email_service.smtplib, "SMTP", classe_smtp)
    return classe_smtp, servidor


@pytest.fixture
def smtp_configurado(monkeypatch):
    monkeypatch.setattr(email_service, "SMTP_HOST", "smtp.exemplo.com")
    monkeypatch.setattr(email_service, "SMTP_PORT", 587)
    monkeypatch.setattr(email_service, "SMTP_USER", "startai@exemplo.com")
    monkeypatch.setattr(email_service, "SMTP_PASSWORD", "senha-de-app")
    monkeypatch.setattr(email_service, "SMTP_FROM", "startai@exemplo.com")
    monkeypatch.setattr(email_service, "FRONTEND_URL", "http://localhost:5173")


def _corpo_do_email(mensagem_bruta: str) -> str:
    parte_texto = message_from_string(mensagem_bruta).get_payload()[0]
    return parte_texto.get_payload(decode=True).decode("utf-8")


def test_deve_autenticar_no_smtp_e_enviar_link_com_o_token(smtp_configurado, smtp_falso):
    # Arrange
    classe_smtp, servidor = smtp_falso

    # Act
    enviar_email_redefinicao_senha(DESTINATARIO, TOKEN)

    # Assert — verifica a interação com a dependência mockada
    classe_smtp.assert_called_once_with("smtp.exemplo.com", 587)
    servidor.starttls.assert_called_once_with()
    servidor.login.assert_called_once_with("startai@exemplo.com", "senha-de-app")
    servidor.sendmail.assert_called_once()
    remetente, destinatario, mensagem = servidor.sendmail.call_args.args
    assert remetente == "startai@exemplo.com"
    assert destinatario == DESTINATARIO
    assert (
        f"http://localhost:5173/reset-password?token={TOKEN}"
        in _corpo_do_email(mensagem)
    )


def test_deve_lancar_erro_e_nao_conectar_quando_smtp_nao_esta_configurado(
    monkeypatch, smtp_falso
):
    # Arrange
    classe_smtp, _ = smtp_falso
    monkeypatch.setattr(email_service, "SMTP_HOST", None)
    monkeypatch.setattr(email_service, "SMTP_USER", None)
    monkeypatch.setattr(email_service, "SMTP_PASSWORD", None)

    # Act
    with pytest.raises(ErroEnvioEmail) as erro:
        enviar_email_redefinicao_senha(DESTINATARIO, TOKEN)

    # Assert — tipo e mensagem da exceção, e nenhuma tentativa de conexão
    assert "SMTP não configurado" in str(erro.value)
    classe_smtp.assert_not_called()


@pytest.mark.parametrize(
    "variavel_ausente", ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
)
def test_deve_recusar_envio_quando_falta_apenas_uma_variavel_de_smtp(
    monkeypatch, smtp_configurado, smtp_falso, variavel_ausente
):
    # Arrange — configuração quase completa: só uma variável está vazia
    classe_smtp, _ = smtp_falso
    monkeypatch.setattr(email_service, variavel_ausente, "")

    # Act
    with pytest.raises(ErroEnvioEmail):
        enviar_email_redefinicao_senha(DESTINATARIO, TOKEN)

    # Assert
    classe_smtp.assert_not_called()
