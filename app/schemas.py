from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Schemas base
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    description: Optional[str] = Field(None, description="Descripción opcional de la tarea")
    completed: bool = Field(False, description="Estado de completitud")


# Schema para crear tareas
class TaskCreate(TaskBase):
    pass


# Schema para actualizar tareas
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


# Schema de respuesta
class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema para respuestas de lista
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    page: int
    size: int


class MessageResponse(BaseModel):
    message: str