from sqlalchemy import Column, Integer, String, LargeBinary
from .database import Base


class FileRecord(Base):
    __tablename__ = "file_records"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    file = Column(LargeBinary)
