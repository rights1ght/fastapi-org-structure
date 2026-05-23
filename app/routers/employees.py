from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import DepartmentNotFound, EmployeeNotFound
from app.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.services import employee as service

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeOut, status_code=201)
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        return service.create_employee(
            db,
            full_name=body.full_name,
            position=body.position,
            department_id=body.department_id,
        )
    except DepartmentNotFound as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[EmployeeOut])
def list_employees(
    department_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_employees(db, department_id=department_id)


@router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = service.get_employee(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: int, body: EmployeeUpdate, db: Session = Depends(get_db)
):
    try:
        return service.update_employee(
            db,
            emp_id,
            full_name=body.full_name,
            position=body.position,
            department_id=body.department_id,
        )
    except EmployeeNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DepartmentNotFound as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    try:
        service.delete_employee(db, emp_id)
    except EmployeeNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
