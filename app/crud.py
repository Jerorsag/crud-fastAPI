from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from . import models, schemas


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Crear una nueva tarea"""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Obtener una tarea por ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        completed: Optional[bool] = None
) -> tuple[List[models.Task], int]:
    """Obtener lista de tareas con paginación y filtros"""
    query = db.query(models.Task)

    # Filtro por búsqueda
    if search:
        query = query.filter(
            or_(
                models.Task.title.contains(search),
                models.Task.description.contains(search)
            )
        )

    # Filtro por estado
    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    # Contar total
    total = query.count()

    # Paginación y ordenamiento
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()

    return tasks, total


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
    """Actualizar una tarea existente"""
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    # Actualizar solo los campos proporcionados
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Eliminar una tarea"""
    db_task = get_task(db, task_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True


def get_task_stats(db: Session) -> dict:
    """Obtener estadísticas de tareas"""
    total = db.query(models.Task).count()
    completed = db.query(models.Task).filter(models.Task.completed == True).count()
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 2)
    }