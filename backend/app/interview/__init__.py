# Módulo do Gabriel — Entrevistador dinâmico (geração e adaptação de perguntas)
#
# Arquivos esperados aqui (mesmo padrão do módulo auth):
#   models.py    -> tabela answers vinculada à sessão de entrevista
#   schemas.py   -> schemas Pydantic (AnswerIn, NextQuestionOut, etc.)
#   service.py   -> lógica de adaptação da próxima pergunta com base na resposta
#   router.py    -> POST /interviews/{id}/answer
#
# Pode ser desenvolvido em paralelo usando respostas mockadas enquanto o
# módulo questions (Leonardo) não estiver pronto.
