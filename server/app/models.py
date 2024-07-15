from sqlalchemy import Column, Integer, String, LargeBinary
from .database import Base
from pydantic import BaseModel

class FileRecord(Base):
    __tablename__ = "file_records"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    file = Column(LargeBinary)

class FileRecordBase(BaseModel):
    name: str
    email: str
    original_filename: str

    class Config:
        orm_mode = True

class FileRecordCreate(FileRecordBase):
    file: bytes

class FileRecordResponse(FileRecordBase):
    id: int