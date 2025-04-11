from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class SyncItem(BaseModel):
    id: str = Field(..., description="ID do item")
    domain: Literal["appointment", "doctor", "address"] = Field(..., description="Domínio do item")
    action: Literal["create", "update", "delete"] = Field(..., description="Ação a ser executada")
    data: Dict[str, Any] = Field(..., description="Dados do item a ser sincronizado")

class ProcessSyncSchema(BaseModel):
    items: List[SyncItem] = Field(..., description="Lista de itens a serem sincronizados")
