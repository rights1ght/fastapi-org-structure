import logging

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.exceptions import DepartmentNotFound, EmployeeNotFound
from app.models.department import Department
from app.models.employee import Employee


def create_employee(
    db: Session, full_name: str, position: str, department_id: int | None = None
) -> Employee:
    if department_id is not None:
        dept = db.query(Department).filter(Department.id == department_id).first()
        if not dept:
            raise DepartmentNotFound(department_id)
    emp = Employee(full_name=full_name, position=position, department_id=department_id)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def get_employee(db: Session, emp_id: int) -> Employee | None:
    return db.query(Employee).filter(Employee.id == emp_id).first()


def get_employees(db: Session, department_id: int | None = None) -> list[Employee]:
    q = db.query(Employee)
    if department_id is not None:
        q = q.filter(Employee.department_id == department_id)
    return q.all()


def update_employee(
    db: Session,
    emp_id: int,
    full_name: str | None = None,
    position: str | None = None,
    department_id: int | None = None,
) -> Employee:
    emp = get_employee(db, emp_id)
    if not emp:
        raise EmployeeNotFound(emp_id)
    if full_name is not None:
        emp.full_name = full_name
    if position is not None:
        emp.position = position
    if department_id is not None:
        emp.department_id = department_id
    db.commit()
    db.refresh(emp)
    return emp


def delete_employee(db: Session, emp_id: int) -> None:
    emp = get_employee(db, emp_id)
    if not emp:
        raise EmployeeNotFound(emp_id)
    db.delete(emp)
    db.commit()
