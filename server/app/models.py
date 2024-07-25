from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from pydantic import BaseModel
from typing import List

class UserRecord(Base):
    __tablename__ = "user_records"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    files = relationship("FileRecord", back_populates="owner")

class FileRecord(Base):
    __tablename__ = "file_records"
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, index=True)
    file = Column(LargeBinary)
    user_id = Column(Integer, ForeignKey("user_records.id"))
    owner = relationship("UserRecord", back_populates="files")

class UserRecordBase(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True

class FileRecordBase(BaseModel):
    original_filename: str

    class Config:
        orm_mode = True

class UserRecordResponse(UserRecordBase):
    id: int
    files: List[FileRecordBase]

    class Config:
        orm_mode = True