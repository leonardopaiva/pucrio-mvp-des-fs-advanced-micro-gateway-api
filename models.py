from pydantic import BaseModel, Field
from typing import Optional, List, Any

class GenericSchema(BaseModel):
    username: Optional[str] = Field(None, description="Nome de usuário")
    password: Optional[str] = Field(None, description="Senha")
    email: Optional[str] = Field(None, description="Email do usuário")
    name: Optional[str] = Field(None, description="Nome completo")
    confirmation_code: Optional[str] = Field(None, description="Código de confirmação")
    session: Optional[str] = Field(None, description="Sessão (opcional)")
    refreshToken: Optional[str] = Field(None, description="Token de refresh")
    items: Optional[List[Any]] = Field(None, description="Lista de itens para sincronização")
    
    class Config:
        extra = "allow"  # Permite campos adicionais que não estão definidos

class AuthHeader(BaseModel):
    authorization: str = Field(
        ...,
        alias="Authorization",
        description="Bearer token para autenticação (formato: 'Bearer <token>')"
    )
