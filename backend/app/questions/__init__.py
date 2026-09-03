# Módulo do Leonardo — Seleção de vaga/tipo de apresentação + perguntas geradas por IA
#
# Arquivos esperados aqui (mesmo padrão do módulo auth):
#   models.py    -> tabela question_sets vinculada a categoria
#   schemas.py   -> schemas Pydantic (CategoryOut, InterviewSessionOut, etc.)
#   service.py   -> integração com a API de LLM para gerar perguntas
#   router.py    -> GET /categories, POST /interviews
#
# Formato de resposta combinado no contrato mínimo do time:
#   {"session_id": "...", "questions": [...]}
