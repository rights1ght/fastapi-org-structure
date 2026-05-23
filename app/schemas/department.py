from pydantic import BaseModel, Field

from app.schemas.employee import EmployeeOut


class DepartmentCreate(BaseModel):
    name: str = Field(..., max_length=200)
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    parent_id: int | None = None


class DepartmentOut(BaseModel):
    id: int
    name: str
    parent_id: int | None

    model_config = {"from_attributes": True}


class DepartmentTree(DepartmentOut):
    children: list["DepartmentTree"] = []
    employees: list[EmployeeOut] = []
    depth: int = 0
