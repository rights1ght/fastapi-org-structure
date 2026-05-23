from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import (
    CircularReferenceError,
    DepartmentNotFound,
    DuplicateNameError,
    ParentNotFound,
    SelfTargetError,
)
from app.schemas.department import DepartmentCreate, DepartmentOut, DepartmentTree, DepartmentUpdate
from app.services import department as service


class DeleteMode(str, Enum):
    cascade = "cascade"
    reassign_parent = "reassign_parent"
    reassign_another = "reassign_another"
    reassign_delete_children = "reassign_delete_children"


router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentOut, status_code=201)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db)):
    try:
        return service.create_department(db, name=body.name, parent_id=body.parent_id)
    except (DuplicateNameError, ParentNotFound) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return service.get_departments(db)


@router.get("/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = service.get_department(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.get("/{dept_id}/tree", response_model=DepartmentTree)
def get_department_tree(
    dept_id: int, depth: int = 1, db: Session = Depends(get_db)
):
    tree = service.get_department_tree(db, dept_id, max_depth=depth)
    if not tree:
        raise HTTPException(status_code=404, detail="Department not found")
    return tree


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: int, body: DepartmentUpdate, db: Session = Depends(get_db)
):
    try:
        return service.update_department(
            db, dept_id, name=body.name, parent_id=body.parent_id
        )
    except DepartmentNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (DuplicateNameError, CircularReferenceError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{dept_id}", status_code=204)
def delete_department(
    dept_id: int,
    mode: DeleteMode = Query(DeleteMode.cascade),
    target_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    if not service.get_department(db, dept_id):
        raise HTTPException(status_code=404, detail="Department not found")

    try:
        if mode == DeleteMode.cascade:
            service.delete_department_cascade(db, dept_id)
        elif mode == DeleteMode.reassign_parent:
            service.delete_department_reassign_parent(db, dept_id)
        elif mode == DeleteMode.reassign_another:
            if target_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="target_id is required for reassign_another mode",
                )
            if not service.get_department(db, target_id):
                raise HTTPException(
                    status_code=400, detail="target_id department not found"
                )
            if target_id == dept_id:
                raise HTTPException(
                    status_code=400,
                    detail="target_id cannot be the same as dept_id",
                )
            service.delete_department_reassign_another(db, dept_id, target_id)
        elif mode == DeleteMode.reassign_delete_children:
            service.delete_department_reassign_delete_children(db, dept_id)
    except DepartmentNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SelfTargetError as e:
        raise HTTPException(status_code=400, detail=str(e))
