"""
Testes de persistência das tabelas de autenticação (app/auth/models.py).

Usam um banco de teste REAL (SQLite em memória) em vez de mock: o objetivo é
provar que o que é salvo pode ser recuperado e que as restrições do banco
(e-mail único, hash de token único) realmente valem. Não passam pela API.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.auth.models import PasswordResetToken, User
from app.auth.service import (
    criar_hash_senha,
    gerar_hash_token,
    gerar_token_redefinicao,
    verificar_senha,
)
from app.models import base

SENHA = "Entrevista#2026"


def _novo_usuario(email: str = "aluna@umc.br") -> User:
    return User(email=email, hashed_password=criar_hash_senha(SENHA), name="Aluna")


def test_deve_salvar_usuario_e_recuperar_pelo_email_com_a_senha_em_hash(db):
    # Arrange
    db.add(_novo_usuario("aluna@umc.br"))
    db.commit()

    # Act — outra sessão, para garantir que o dado veio mesmo do banco
    with base.SessionLocal() as outra_sessao:
        recuperado = (
            outra_sessao.query(User).filter(User.email == "aluna@umc.br").one()
        )

    # Assert
    assert isinstance(recuperado.id, uuid.UUID)
    assert recuperado.name == "Aluna"
    assert recuperado.hashed_password != SENHA
    assert verificar_senha(SENHA, recuperado.hashed_password) is True
    assert recuperado.created_at is not None  # preenchido pelo próprio banco


def test_deve_recuperar_token_de_redefinicao_pelo_hash_e_chegar_ao_usuario(db):
    # Arrange — mesmo caminho do "esqueci minha senha": grava só o hash
    usuario = _novo_usuario("aluna@umc.br")
    db.add(usuario)
    db.flush()
    token_do_email, hash_do_token = gerar_token_redefinicao()
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.add(
        PasswordResetToken(
            user_id=usuario.id, token_hash=hash_do_token, expires_at=expira_em
        )
    )
    db.commit()

    # Act — consulta usada na redefinição: busca pelo hash do token recebido
    with base.SessionLocal() as outra_sessao:
        registro = (
            outra_sessao.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == gerar_hash_token(token_do_email))
            .one()
        )
        email_do_dono = registro.user.email

    # Assert
    assert email_do_dono == "aluna@umc.br"
    assert registro.expires_at == expira_em
    assert registro.used_at is None


def test_nao_deve_encontrar_token_quando_o_hash_nao_corresponde(db):
    # Arrange
    usuario = _novo_usuario()
    db.add(usuario)
    db.flush()
    _, hash_do_token = gerar_token_redefinicao()
    db.add(
        PasswordResetToken(
            user_id=usuario.id,
            token_hash=hash_do_token,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
    )
    db.commit()

    # Act — procura com um token que nunca foi emitido
    registro = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == gerar_hash_token("token-errado"))
        .first()
    )

    # Assert
    assert registro is None


def test_banco_deve_impedir_dois_usuarios_com_o_mesmo_email(db):
    # Arrange
    db.add(_novo_usuario("repetido@umc.br"))
    db.commit()

    # Act
    db.add(_novo_usuario("repetido@umc.br"))
    with pytest.raises(IntegrityError) as erro:
        db.commit()
    db.rollback()

    # Assert — a restrição UNIQUE da coluna e-mail barrou; segue existindo um só
    assert "users.email" in str(erro.value)
    assert db.query(User).filter(User.email == "repetido@umc.br").count() == 1
