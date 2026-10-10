"""
Testes unitários das regras de autenticação (app/auth/service.py):
hash de senha (bcrypt), token de acesso (JWT) e token de redefinição de senha.

São funções puras: não usam banco nem rede. Nenhum teste fica esperando o
tempo passar: o token expirado já é criado com a data de expiração no
passado.
"""
import hashlib
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth.service import (
    ALGORITHM,
    SECRET_KEY,
    criar_hash_senha,
    criar_token_acesso,
    decodificar_token_acesso,
    gerar_hash_token,
    gerar_token_redefinicao,
    verificar_senha,
)

ID_USUARIO = "0b0f7a52-6f0e-4c58-9d0c-2f3d6a7b8c9d"
SENHA = "Entrevista#2026"


def _token_que_expira_em(segundos: int) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(seconds=segundos)
    return jwt.encode({"sub": ID_USUARIO, "exp": expira_em}, SECRET_KEY, algorithm=ALGORITHM)


# --- Token de acesso (JWT) ---------------------------------------------------


def test_deve_devolver_o_id_do_usuario_quando_token_e_valido():
    # Arrange
    token = criar_token_acesso(id_usuario=ID_USUARIO)

    # Act
    id_decodificado = decodificar_token_acesso(token)

    # Assert
    assert id_decodificado == ID_USUARIO


def test_deve_recusar_token_assinado_com_outra_chave():
    # Arrange — alguém forjou um token sem conhecer a JWT_SECRET_KEY
    token_forjado = jwt.encode(
        {"sub": ID_USUARIO, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "chave-do-atacante",
        algorithm=ALGORITHM,
    )

    # Act
    id_decodificado = decodificar_token_acesso(token_forjado)

    # Assert
    assert id_decodificado is None


def test_deve_recusar_token_expirado_ha_um_segundo():
    # Arrange — fronteira da validade: venceu há 1 segundo
    token_vencido = _token_que_expira_em(-1)

    # Act
    id_decodificado = decodificar_token_acesso(token_vencido)

    # Assert
    assert id_decodificado is None


def test_deve_recusar_texto_que_nao_e_um_jwt():
    # Arrange
    texto_qualquer = "isto-nao-e-um-token"

    # Act
    id_decodificado = decodificar_token_acesso(texto_qualquer)

    # Assert
    assert id_decodificado is None


# --- Hash de senha (bcrypt) --------------------------------------------------


def test_deve_gerar_hash_diferente_da_senha_e_reconhecer_a_senha_correta():
    # Arrange / Act
    senha_hash = criar_hash_senha(SENHA)

    # Assert
    assert senha_hash != SENHA
    assert verificar_senha(SENHA, senha_hash) is True


def test_deve_recusar_senha_diferente_da_cadastrada():
    # Arrange
    senha_hash = criar_hash_senha(SENHA)

    # Act
    confere = verificar_senha("Entrevista#2027", senha_hash)

    # Assert
    assert confere is False


def test_deve_gerar_hashes_diferentes_para_a_mesma_senha():
    # Arrange / Act — o "salt" aleatório impede que senhas iguais fiquem
    # com o mesmo hash no banco
    primeiro_hash = criar_hash_senha(SENHA)
    segundo_hash = criar_hash_senha(SENHA)

    # Assert
    assert primeiro_hash != segundo_hash


# --- Token de redefinição de senha -------------------------------------------


def test_deve_gerar_token_de_redefinicao_cujo_hash_e_o_sha256_do_token_enviado():
    # Act
    token_do_email, hash_do_banco = gerar_token_redefinicao()

    # Assert — o banco guarda só o hash; o token puro vai apenas no e-mail
    assert hash_do_banco != token_do_email
    assert hash_do_banco == hashlib.sha256(token_do_email.encode()).hexdigest()
    assert gerar_hash_token(token_do_email) == hash_do_banco


def test_deve_gerar_tokens_de_redefinicao_diferentes_a_cada_pedido():
    # Act
    primeiro_token, _ = gerar_token_redefinicao()
    segundo_token, _ = gerar_token_redefinicao()

    # Assert
    assert primeiro_token != segundo_token
