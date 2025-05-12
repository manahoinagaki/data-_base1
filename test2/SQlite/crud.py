from sqlalchemy.orm import Session, selectinload
from . import models, schemas, security
import hashlib # パスワードハッシュ化用

# データベース操作関数

# ------ タスク操作 ------

# タスクを作成
def create_task(db: Session,organization_id: int, task: schemas.TaskCreate):
    new_task = models.Task(**task.dict(), organization_id=organization_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# タスク一覧を取得
def get_tasks(db: Session, organization_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Task)\
        .options(
            selectinload(models.Task.assignee), # selectinload → assignee（担当者）とorganization（組織）だけ別SQLで高速取得してくれる
            selectinload(models.Task.organization)
        )\
        .filter(models.Task.organization_id == organization_id).offset(skip).limit(limit).all()

# タスクを取得
def get_task(db: Session, task_id: int):
    return db.query(models.Task)\
        .options(
            selectinload(models.Task.assignee),
            selectinload(models.Task.organization)
        )\
        .filter(models.Task.id == task_id)\
        .first()

# タスクを更新
def update_task(db: Session, task_id: int, task_data: schemas.TaskUpdate):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        for key, value in task_data.dict(exclude_unset=True).items():
            setattr(task, key, value)  # ✅ None の値を更新しないようにする
        db.commit()
        db.refresh(task)
    return task

# タスクを削除
def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task
