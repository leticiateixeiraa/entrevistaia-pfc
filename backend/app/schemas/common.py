"""
Schemas compartilhados entre módulos.
Formato de erro padrão combinado no "contrato mínimo" do roteiro:
    {"detail": "mensagem"}
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
