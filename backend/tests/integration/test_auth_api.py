"""
Testes de integração dos endpoints de autenticação (app/auth/router.py).

Cada requisição atravessa as camadas de verdade: rota FastAPI -> validação
(schemas) -> regras (service) -> banco de teste. O único ponto substituído é
o serviço externo de e-mail (SMTP).
"""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from app.auth import email_service
from app.auth.models import PasswordResetToken, User

from tests.integration.conftest import SENHA_PADRAO

EMAIL = "aluna@umc.br"
NOVA_SENHA = "NovaSenha#2027"


# --- Endpoint: caminho feliz (status + corpo) --------------------------------


def test_deve_retornar_201_e_somente_os_dados_publicos_ao_cadastrar(client):
    # Arrange
    cadastro = {
        "email": EMAIL,
        "password": SENHA_PADRAO,
        "name": "Aluna de Teste",
        "terms_accepted": True,
    }

    # Act
    resposta = client.post("/auth/register", json=cadastro)

    # Assert
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == EMAIL
    assert corpo["name"] == "Aluna de Teste"
    assert uuid.UUID(corpo["id"])  # id gerado é um UUID válido
    # a senha (nem o hash dela) nunca volta na resposta
    assert set(corpo) == {"id", "email", "name"}


# --- Endpoint: erros 4xx (status + corpo de erro) ----------------------------


def test_deve_retornar_422_explicar_a_regra_e_nao_criar_conta_quando_senha_e_fraca(
    client, db
):
    # Arrange — senha sem caractere especial
    cadastro = {"email": EMAIL, "password": "SemEspecial2026", "terms_accepted": True}

    # Act
    resposta = client.post("/auth/register", json=cadastro)

    # Assert
    assert resposta.status_code == 422
    erro = resposta.json()["detail"][0]
    assert erro["loc"] == ["body", "password"]
    assert "caractere especial" in erro["msg"]
    assert db.query(User).count() == 0


def test_deve_retornar_401_identico_para_senha_errada_e_para_email_inexistente(
    client, cadastrar
):
    # Arrange
    cadastrar(email=EMAIL)

    # Act
    senha_errada = client.post(
        "/auth/login", json={"email": EMAIL, "password": "SenhaErrada#1"}
    )
    email_inexistente = client.post(
        "/auth/login", json={"email": "ninguem@umc.br", "password": SENHA_PADRAO}
    )

    # Assert — respostas iguais: não dá para descobrir quais e-mails têm conta
    assert senha_errada.status_code == 401
    assert email_inexistente.status_code == 401
    assert senha_errada.json() == {"detail": "E-mail ou senha inválidos"}
    assert email_inexistente.json() == senha_errada.json()


def test_deve_retornar_401_em_rota_protegida_quando_token_e_invalido(client):
    # Arrange
    cabecalho = {"Authorization": "Bearer token-inventado"}

    # Act
    resposta = client.get("/auth/me", headers=cabecalho)

    # Assert
    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "Token inválido ou expirado"}
    assert resposta.headers["WWW-Authenticate"] == "Bearer"


def test_deve_retornar_400_quando_link_de_redefinicao_nao_existe(client):
    # Arrange
    pedido = {"token": "token-que-nunca-foi-emitido", "new_password": NOVA_SENHA}

    # Act
    resposta = client.post("/auth/reset-password", json=pedido)

    # Assert
    assert resposta.status_code == 400
    assert resposta.json() == {
        "detail": "Link inválido ou expirado. Solicite uma nova redefinição."
    }


# --- Falha do serviço externo de e-mail ---------------------------------------


def test_deve_retornar_502_quando_servico_de_email_nao_esta_configurado(
    client, cadastrar, monkeypatch
):
    # Arrange — usuário existe, mas o SMTP não foi configurado
    cadastrar(email=EMAIL)
    monkeypatch.setattr(email_service, "SMTP_HOST", None)
    monkeypatch.setattr(email_service, "SMTP_USER", None)
    monkeypatch.setattr(email_service, "SMTP_PASSWORD", None)

    # Act
    resposta = client.post("/auth/forgot-password", json={"email": EMAIL})

    # Assert — 502: a falha é do serviço externo, não da API
    assert resposta.status_code == 502
    assert resposta.json() == {
        "detail": "Não foi possível enviar o e-mail agora. Tente de novo mais tarde."
    }


# --- API + banco: o que fica gravado ao pedir a redefinição ------------------


def test_deve_gravar_somente_o_hash_do_token_com_validade_de_30_minutos(
    client, cadastrar, emails_enviados, db
):
    # Arrange
    cadastrar(email=EMAIL)
    antes = datetime.now(timezone.utc)

    # Act
    resposta = client.post("/auth/forgot-password", json={"email": EMAIL})

    # Assert
    depois = datetime.now(timezone.utc)
    assert resposta.status_code == 200
    destinatario, token_do_email = emails_enviados[0]
    assert destinatario == EMAIL

    registro = db.query(PasswordResetToken).one()
    assert registro.token_hash == hashlib.sha256(token_do_email.encode()).hexdigest()
    assert registro.token_hash != token_do_email  # o token puro não vai para o banco
    assert registro.used_at is None
    assert (
        antes + timedelta(minutes=30)
        <= registro.expires_at
        <= depois + timedelta(minutes=30)
    )


def test_nao_deve_gerar_token_nem_enviar_email_para_email_sem_conta(
    client, emails_enviados, db
):
    # Arrange — banco vazio: ninguém cadastrado

    # Act
    resposta = client.post("/auth/forgot-password", json={"email": "ninguem@umc.br"})

    # Assert — a resposta é a mesma de um e-mail cadastrado, mas nada acontece
    assert resposta.status_code == 200
    assert resposta.json() == {
        "message": "Se esse e-mail estiver cadastrado, você vai receber um link de redefinição."
    }
    assert emails_enviados == []
    assert db.query(PasswordResetToken).count() == 0


# --- Fluxos completos: API -> service -> banco -> API -------------------------


def test_fluxo_completo_cadastrar_entrar_e_consultar_o_proprio_perfil(client):
    # Arrange / Act 1 — cadastra
    cadastro = client.post(
        "/auth/register",
        json={
            "email": EMAIL,
            "password": SENHA_PADRAO,
            "name": "Aluna de Teste",
            "terms_accepted": True,
        },
    )

    # Act 2 — entra com a mesma senha e recebe o token
    login = client.post("/auth/login", json={"email": EMAIL, "password": SENHA_PADRAO})
    token = login.json()["access_token"]

    # Act 3 — usa o token para consultar o recurso criado
    perfil = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    # Assert — o perfil consultado é exatamente o usuário criado no passo 1
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert perfil.status_code == 200
    assert perfil.json() == cadastro.json()


def test_fluxo_completo_de_recuperacao_de_senha_troca_a_senha_e_invalida_o_link(
    client, cadastrar, emails_enviados
):
    # Arrange — usuária cadastrada pede a redefinição e "recebe" o e-mail
    cadastrar(email=EMAIL, senha=SENHA_PADRAO)
    client.post("/auth/forgot-password", json={"email": EMAIL})
    _, token_do_email = emails_enviados[0]

    # Act — usa o link do e-mail para definir a nova senha
    redefinicao = client.post(
        "/auth/reset-password",
        json={"token": token_do_email, "new_password": NOVA_SENHA},
    )

    # Assert — senha nova entra, senha antiga não entra, link não serve de novo
    assert redefinicao.status_code == 200
    assert redefinicao.json() == {"message": "Senha redefinida com sucesso."}

    login_senha_nova = client.post(
        "/auth/login", json={"email": EMAIL, "password": NOVA_SENHA}
    )
    login_senha_antiga = client.post(
        "/auth/login", json={"email": EMAIL, "password": SENHA_PADRAO}
    )
    reuso_do_link = client.post(
        "/auth/reset-password",
        json={"token": token_do_email, "new_password": "OutraSenha#2028"},
    )
    assert login_senha_nova.status_code == 200
    assert login_senha_antiga.status_code == 401
    assert reuso_do_link.status_code == 400
