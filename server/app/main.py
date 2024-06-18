from fastapi import FastAPI, UploadFile, File, status, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class FileRecord(BaseModel):
    name: str
    email: str
    file_path: bytes


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/forms")
def read_upload(db: Session = Depends(get_db)):
    all_forms = db.query(models.Upload).all()
    return {"Todos Formulários de Contato": all_forms}


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    new_user: FileRecord, file: UploadFile = File(...), db: Session = Depends(get_db)
):

    try:
        contents = await file.read()

        form_create = models.FileRecord(
            name=new_user.name, email=new_user.email, file_path=contents
        )
        db.add(form_create)
        db.commit()
        db.refresh(form_create)

        return {"Usuário Criado": form_create}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
