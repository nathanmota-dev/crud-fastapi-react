from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from pydantic import BaseModel
<<<<<<< HEAD
from typing import List

class UserRecord(Base):
    __tablename__ = "user_records"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    files = relationship("FileRecord", back_populates="owner")
=======
>>>>>>> 5a725cea4d7b974d20bdafbd186856e8be5549c1

class FileRecord(Base):
    __tablename__ = "file_records"
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, index=True)
    file = Column(LargeBinary)
<<<<<<< HEAD
    user_id = Column(Integer, ForeignKey("user_records.id"))
    owner = relationship("UserRecord", back_populates="files")

class UserRecordBase(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True

class FileRecordBase(BaseModel):
=======

class FileRecordBase(BaseModel):
    name: str
    email: str
>>>>>>> 5a725cea4d7b974d20bdafbd186856e8be5549c1
    original_filename: str

    class Config:
        orm_mode = True

<<<<<<< HEAD
class UserRecordResponse(UserRecordBase):
    id: int
    files: List[FileRecordBase]

    class Config:
        orm_mode = True
=======
class FileRecordCreate(FileRecordBase):
    file: bytes

class FileRecordResponse(FileRecordBase):
    id: int
>>>>>>> 5a725cea4d7b974d20bdafbd186856e8be5549c1
