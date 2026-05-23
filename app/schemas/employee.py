from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    full_name: str = Field(..., max_length=200)
    position: str = Field(..., max_length=200)
    department_id: int | None = None


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=200)
    department_id: int | None = None


class EmployeeOut(BaseModel):
    id: int
    full_name: str
    position: str
    department_id: int | None

    model_config = {"from_attributes": True}
