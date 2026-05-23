import logging
from collections import defaultdict

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.exceptions import (
    CircularReferenceError,
    DepartmentNotFound,
    DuplicateNameError,
    ParentNotFound,
    SelfTargetError,
)
from app.models.department import Department
from app.models.employee import Employee


def _check_duplicate_name(
    db: Session, name: str, parent_id: int | None, exclude_id: int | None = None
) -> None:
    query = db.query(Department).filter(
        Department.name == name,
        Department.parent_id == parent_id,
    )
    if exclude_id is not None:
        query = query.filter(Department.id != exclude_id)
    if query.first():
        raise DuplicateNameError(name, parent_id)


def _check_cycle(db: Session, dept_id: int, new_parent_id: int | None) -> None:
    if new_parent_id is None:
        return
    if new_parent_id == dept_id:
        raise CircularReferenceError("Department cannot be its own parent")
    current = db.query(Department).filter(Department.id == new_parent_id).first()
    while current is not None:
        if current.id == dept_id:
            raise CircularReferenceError("Circular reference detected")
        current = (
            db.query(Department).filter(Department.id == current.parent_id).first()
            if current.parent_id is not None
            else None
        )


def create_department(db: Session, name: str, parent_id: int | None = None) -> Department:
    _check_duplicate_name(db, name, parent_id)
    if parent_id is not None and not get_department(db, parent_id):
        raise ParentNotFound(parent_id)
    dept = Department(name=name, parent_id=parent_id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def get_department(db: Session, dept_id: int) -> Department | None:
    return db.query(Department).filter(Department.id == dept_id).first()


def get_departments(db: Session) -> list[Department]:
    return db.query(Department).all()


def update_department(
    db: Session, dept_id: int, name: str | None = None, parent_id: int | None = None
) -> Department:
    dept = get_department(db, dept_id)
    if not dept:
        raise DepartmentNotFound(dept_id)
    if name is not None:
        final_parent = parent_id if parent_id is not None else dept.parent_id
        _check_duplicate_name(db, name, final_parent, exclude_id=dept_id)
        dept.name = name
    if parent_id is not None:
        _check_cycle(db, dept_id, parent_id)
        dept.parent_id = parent_id
    db.commit()
    db.refresh(dept)
    return dept


def _collect_descendant_ids(root_id: int, children_map: dict[int | None, list[Department]]) -> set[int]:
    ids = {root_id}
    stack = [root_id]
    while stack:
        pid = stack.pop()
        for child in children_map.get(pid, []):
            if child.id not in ids:
                ids.add(child.id)
                stack.append(child.id)
    return ids


def delete_department_cascade(db: Session, dept_id: int) -> None:
    if not get_department(db, dept_id):
        raise DepartmentNotFound(dept_id)
    all_depts = db.query(Department).all()
    children_map = _build_children_map(all_depts)
    descendant_ids = _collect_descendant_ids(dept_id, children_map)
    db.query(Employee).filter(Employee.department_id.in_(descendant_ids)).delete(
        synchronize_session=False
    )
    db.query(Department).filter(Department.id.in_(descendant_ids)).delete(
        synchronize_session=False
    )
    db.commit()


def delete_department_reassign_parent(db: Session, dept_id: int) -> None:
    dept = get_department(db, dept_id)
    if not dept:
        raise DepartmentNotFound(dept_id)
    parent_id = dept.parent_id
    db.query(Employee).filter(Employee.department_id == dept_id).update(
        {"department_id": parent_id}, synchronize_session=False
    )
    db.query(Department).filter(Department.parent_id == dept_id).update(
        {"parent_id": parent_id}, synchronize_session=False
    )
    db.delete(dept)
    db.commit()


def delete_department_reassign_another(db: Session, dept_id: int, target_id: int) -> None:
    dept = get_department(db, dept_id)
    if not dept:
        raise DepartmentNotFound(dept_id)
    if target_id == dept_id:
        raise SelfTargetError("target_id cannot be the same as dept_id")
    db.query(Employee).filter(Employee.department_id == dept_id).update(
        {"department_id": target_id}, synchronize_session=False
    )
    db.query(Department).filter(Department.parent_id == dept_id).update(
        {"parent_id": target_id}, synchronize_session=False
    )
    db.delete(dept)
    db.commit()


def delete_department_reassign_delete_children(db: Session, dept_id: int) -> None:
    dept = get_department(db, dept_id)
    if not dept:
        raise DepartmentNotFound(dept_id)
    parent_id = dept.parent_id
    all_depts = db.query(Department).all()
    children_map = _build_children_map(all_depts)
    descendant_ids = _collect_descendant_ids(dept_id, children_map)
    descendant_ids.discard(dept_id)

    db.query(Employee).filter(Employee.department_id == dept_id).update(
        {"department_id": parent_id}, synchronize_session=False
    )
    db.query(Employee).filter(Employee.department_id.in_(descendant_ids)).delete(
        synchronize_session=False
    )
    db.query(Department).filter(Department.id.in_(descendant_ids)).delete(
        synchronize_session=False
    )
    db.delete(dept)
    db.commit()


def _build_tree(
    dept: Department,
    children_map: dict[int | None, list[Department]],
    employees_map: dict[int, list[dict]],
    depth: int,
    max_depth: int,
) -> dict:
    node = {
        "id": dept.id,
        "name": dept.name,
        "parent_id": dept.parent_id,
        "employees": employees_map.get(dept.id, []),
        "children": [],
        "depth": depth,
    }
    if depth < max_depth:
        for child in children_map.get(dept.id, []):
            node["children"].append(
                _build_tree(child, children_map, employees_map, depth + 1, max_depth)
            )
    return node


def _build_children_map(depts: list[Department]) -> dict[int | None, list[Department]]:
    children_map: dict[int | None, list[Department]] = defaultdict(list)
    for d in depts:
        children_map[d.parent_id].append(d)
    return children_map


# TODO: вынести построение дерева в отдельный утилитарный модуль,
# сейчас логика перемешана с удалением
def get_department_tree(db: Session, dept_id: int, max_depth: int = 1) -> dict | None:
    dept = get_department(db, dept_id)
    if not dept:
        return None
    max_depth = max(1, min(max_depth, 5))

    all_depts = db.query(Department).all()
    children_map = _build_children_map(all_depts)

    dept_ids_in_subtree = _collect_descendant_ids(dept_id, children_map)
    employees = (
        db.query(Employee)
        .filter(Employee.department_id.in_(dept_ids_in_subtree))
        .all()
    )
    employees_map: dict[int, list[dict]] = defaultdict(list)
    for emp in employees:
        employees_map[emp.department_id].append(
            {"id": emp.id, "full_name": emp.full_name, "position": emp.position, "department_id": emp.department_id}
        )

    return _build_tree(dept, children_map, employees_map, 0, max_depth)
