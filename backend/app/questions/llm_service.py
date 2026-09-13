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
