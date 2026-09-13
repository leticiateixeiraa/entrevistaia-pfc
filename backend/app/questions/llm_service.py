import json
import os

from google import genai
from google.genai import types


class LLMGenerationError(RuntimeError):
    pass


def generate_questions(
    job_title: str,
    presentation_type: str,
    job_description: str | None,
) -> list[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMGenerationError(
            "GEMINI_API_KEY não configurada. Adicione uma chave do Gemini no arquivo backend/.env."
        )

    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    prompt = (
        "Analise a vaga abaixo e crie de 4 a 6 perguntas de entrevista em "
        "portugues do Brasil.\n\n"
        f"Cargo: {job_title}\n"
        f"Tipo de entrevista: {presentation_type}\n"
        f"Descricao da vaga:\n{job_description or 'Nao informada'}\n\n"
        "As perguntas devem avaliar competencias, responsabilidades e contexto "
        "especificos da vaga. Evite perguntas genericas quando a descricao trouxer "
        "detalhes. Gere exatamente 5 perguntas. Retorne somente JSON valido no formato: "
        '{"questions": ["pergunta 1", "pergunta 2"]}'
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Voce e um entrevistador tecnico experiente e objetivo."
                ),
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )
        content = response.text or "{}"
        questions = json.loads(content).get("questions")
    except Exception as error:
        raise LLMGenerationError("Nao foi possivel gerar perguntas com o LLM") from error

    if not isinstance(questions, list):
        raise LLMGenerationError("O LLM retornou um formato de perguntas invalido")

    cleaned = [
        question.strip()
        for question in questions
        if isinstance(question, str) and question.strip()
    ]
    if len(cleaned) < 5:
        raise LLMGenerationError("O LLM retornou menos de 5 perguntas")
    return cleaned[:5]


def generate_adapted_question(
    current_question: str,
    answer_text: str,
    previous_answers: list[tuple[str, str]],
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMGenerationError(
            "GEMINI_API_KEY não configurada. Adicione uma chave do Gemini no arquivo backend/.env."
        )

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    history = "\n".join(
        f"Pergunta: {question}\nResposta: {answer}"
        for question, answer in previous_answers
    )
    prompt = (
        "Crie a próxima pergunta de uma entrevista em português do Brasil. "
        "Adapte-a ao conteúdo da resposta atual e ao histórico, aprofundando "
        "um ponto relevante sem repetir perguntas. Retorne somente JSON válido "
        'no formato {"question": "..."}.\n\n'
        f"Histórico:\n{history or 'Nenhum'}\n\n"
        f"Pergunta atual: {current_question}\n"
        f"Resposta atual: {answer_text}"
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Você é um entrevistador atento. Faça uma pergunta por vez, "
                    "clara, específica e diretamente relacionada à resposta."
                ),
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )
        question = json.loads(response.text or "{}").get("question")
    except Exception as error:
        raise LLMGenerationError("Não foi possível adaptar a próxima pergunta") from error

    if not isinstance(question, str) or not question.strip():
        raise LLMGenerationError("O LLM retornou uma pergunta adaptada inválida")
    return question.strip()
