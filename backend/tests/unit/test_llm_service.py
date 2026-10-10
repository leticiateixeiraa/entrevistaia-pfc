"""Testes unitários da geração de perguntas com o Gemini."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.questions import llm_service
from app.questions.llm_service import LLMGenerationError, generate_questions


def _resposta_com_perguntas(perguntas):
    return SimpleNamespace(text=json.dumps({"questions": perguntas}))


def test_deve_gerar_cinco_perguntas_e_limpar_espacos(monkeypatch):
    cliente = MagicMock()
    cliente.models.generate_content.return_value = _resposta_com_perguntas(
        ["  Pergunta 1  ", "Pergunta 2", " ", "Pergunta 3", "Pergunta 4", "Pergunta 5", "Pergunta 6"]
    )
    criar_cliente = MagicMock(return_value=cliente)
    monkeypatch.setattr(llm_service.genai, "Client", criar_cliente)
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")

    perguntas = generate_questions(
        job_title="Desenvolvedor Python",
        presentation_type="tecnica",
        job_description="Desenvolver APIs.",
    )

    assert perguntas == [
        "Pergunta 1",
        "Pergunta 2",
        "Pergunta 3",
        "Pergunta 4",
        "Pergunta 5",
    ]
    criar_cliente.assert_called_once_with(api_key="chave-de-teste")
    cliente.models.generate_content.assert_called_once()


def test_deve_usar_regra_mista_para_tipo_de_entrevista_desconhecido(monkeypatch):
    cliente = MagicMock()
    cliente.models.generate_content.return_value = _resposta_com_perguntas(
        [f"Pergunta {numero}" for numero in range(1, 6)]
    )
    monkeypatch.setattr(llm_service.genai, "Client", MagicMock(return_value=cliente))
    monkeypatch.setattr(llm_service, "_generate_content", MagicMock(
        return_value=cliente.models.generate_content.return_value
    ))
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")

    generate_questions("Analista", "tipo-inexistente", None)

    prompt = llm_service._generate_content.call_args.args[2]
    assert llm_service.INTERVIEW_RULES["mista"] in prompt
    assert "Nao informada" in prompt


def test_deve_recusar_geracao_sem_chave_do_gemini(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(LLMGenerationError, match="GEMINI_API_KEY não configurada"):
        generate_questions("Desenvolvedor", "mista", None)


def test_deve_recusar_resposta_com_menos_de_cinco_perguntas(monkeypatch):
    cliente = MagicMock()
    cliente.models.generate_content.return_value = _resposta_com_perguntas(
        ["Pergunta 1", "Pergunta 2", "Pergunta 3", "Pergunta 4"]
    )
    monkeypatch.setattr(llm_service.genai, "Client", MagicMock(return_value=cliente))
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")

    with pytest.raises(LLMGenerationError, match="menos de 5 perguntas"):
        generate_questions("Desenvolvedor", "mista", "Criar APIs")
