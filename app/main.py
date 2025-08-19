from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import math

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

# Crear las tablas
models.Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="Task CRUD API",
    description="Una API simple para gestión de tareas con FastAPI y MySQL",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints

@app.get("/", response_model=schemas.MessageResponse)
async def root():
    """Endpoint de bienvenida"""
    return {"message": "🚀 Task CRUD API está funcionando correctamente!"}


@app.get("/health", response_model=schemas.MessageResponse)
async def health_check():
    """Health check para Railway"""
    return {"message": "API is healthy"}


@app.post("/create-task/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Crear una nueva tarea"""
    try:
        return crud.create_task(db=db, task=task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la tarea: {str(e)}")


@app.get("/tasks/", response_model=schemas.TaskListResponse)
async def read_tasks(
        skip: int = Query(0, ge=0, description="Elementos a saltar"),
        limit: int = Query(20, ge=1, le=100, description="Límite de elementos"),
        search: Optional[str] = Query(None, description="Buscar en título y descripción"),
        completed: Optional[bool] = Query(None, description="Filtrar por estado"),
        db: Session = Depends(get_db)
):
    """Obtener lista de tareas con paginación y filtros"""
    try:
        tasks, total = crud.get_tasks(db, skip=skip, limit=limit, search=search, completed=completed)

        return schemas.TaskListResponse(
            tasks=tasks,
            total=total,
            page=math.ceil(skip / limit) + 1 if limit > 0 else 1,
            size=len(tasks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las tareas: {str(e)}")


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def read_task(task_id: int, db: Session = Depends(get_db)):
    """Obtener una tarea específica"""
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return db_task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Actualizar una tarea existente"""
    db_task = crud.update_task(db, task_id=task_id, task_update=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return db_task


@app.delete("/tasks/{task_id}", response_model=schemas.MessageResponse)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Eliminar una tarea"""
    success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": f"Tarea {task_id} eliminada correctamente"}


@app.get("/tasks/stats/summary")
async def get_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de las tareas"""
    try:
        return crud.get_task_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


# Manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {"error": "Error interno del servidor", "detail": str(exc)}