from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    department = relationship("Department", back_populates="employees")

    def __repr__(self):
        return f"<Employee id={self.id} name='{self.full_name}'>"
