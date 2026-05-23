from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    children = relationship(
        "Department",
        backref="parent",
        remote_side="Department.id",
    )

    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department id={self.id} name='{self.name}'>"
