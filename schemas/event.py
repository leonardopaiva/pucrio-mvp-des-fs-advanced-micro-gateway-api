from datetime import datetime
from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class EventType(Enum):
    CONSULTATION = 1
    EXAM = 2

class EventSchema(BaseModel):
    """
    Defines how a new event to be inserted should be represented.
    The "id" field is optional, as it can be generated automatically (e.g., UUID).
    """
    id: Optional[str] = Field(None, description="Event ID (automatically generated if not provided)")
    name: str = Field("Consulta Dermatologista", description="Name of the event")
    description: str = Field("A consulta será por ordem de chegada", description="Description of the event")
    observation: str = Field("Vou precisar de ajuda para ir até a consulta porque o carro está quebrado",
                             description="Observation regarding the event")
    date: datetime = Field(default_factory=datetime.now, description="Event date and time")
    doctor_name: str = Field("Doutor Matheus", description="Doctor's name")
    location_name: str = Field("memorial são jose recife 83", description="Location name")
    location_id: int = Field(1, description="Location ID")
    doctor_id: int = Field(1, description="Doctor ID")
    user_id: str = Field("default_user_id", description="User ID associated with the event")
    type: EventType = Field(EventType.CONSULTATION, description="Type of the event (e.g., CONSULTATION or EXAM)")

class EventBuscaSchema(BaseModel):
    """
    Defines the structure representing a search,
    using the "id" and "user_id" fields.
    """
    id: str = Field("1", description="Event ID to be searched")
    user_id: str = Field("54e8a4a8-5001-7018-8eec-ce6b634cded9", description="User ID of the event owner")

class EventBuscaIdSchema(BaseModel):
    """
    Defines the structure representing a search based solely on the event ID.
    """
    id: str = Field("1", description="Event ID")

class ListagemEventsSchema(BaseModel):
    """
    Defines how a listing of events will be returned.
    """
    events: List[EventSchema] = Field(..., description="List of events")

class EventViewSchema(BaseModel):
    """
    Defines how an event will be returned, including comments.
    """
    id: str = Field("1", description="Event ID")
    name: str = Field("Consulta Dermatologista", description="Name of the event")
    description: str = Field("A consulta será por ordem de chegada", description="Description of the event")
    observation: str = Field("Vou precisar de ajuda para ir até a consulta porque o carro está quebrado",
                             description="Event observation")
    date: datetime = Field(default_factory=datetime.now, description="Event date and time")
    doctor_name: str = Field("Doutor Matheus", description="Doctor's name")
    location_name: str = Field("memorial são jose recife 83", description="Location name")
    location_id: int = Field(1, description="Location ID")
    doctor_id: int = Field(1, description="Doctor ID")
    user_id: str = Field("default_user_id", description="User ID associated with the event")
    type: EventType = Field(EventType.CONSULTATION, description="Type of the event")
    total_cometarios: int = Field(1, description="Total comments associated with the event")
    comentarios: List[Any] = Field([], description="List of comments (each comment can be represented as a dictionary)")

class EventDelSchema(BaseModel):
    """
    Defines the structure of the data returned after a removal request.
    """
    mesage: str = Field(..., description="Return message")
    name: str = Field(..., description="Name of the removed event")
