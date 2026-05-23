class DepartmentNotFound(Exception):
    def __init__(self, dept_id: int):
        self.dept_id = dept_id
        super().__init__(f"Department (id={dept_id}) not found")


class EmployeeNotFound(Exception):
    def __init__(self, emp_id: int):
        self.emp_id = emp_id
        super().__init__(f"Employee (id={emp_id}) not found")


class ParentNotFound(Exception):
    def __init__(self, parent_id: int):
        self.parent_id = parent_id
        super().__init__(f"Parent department (id={parent_id}) not found")


class DuplicateNameError(Exception):
    def __init__(self, name: str, parent_id: int | None):
        self.name = name
        self.parent_id = parent_id
        super().__init__(
            f"Department with name '{name}' already exists under parent_id={parent_id}"
        )


class CircularReferenceError(Exception):
    pass


class SelfTargetError(Exception):
    pass
