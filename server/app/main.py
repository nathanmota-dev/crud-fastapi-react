from fastapi import FastAPI, File, Form, UploadFile, Depends
from fastapi.responses import JSONResponse
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/upload")
def read_upload(db: Session = Depends(get_db)):
    all_users = db.query(models.Upload).all()
    return {"Todos Usuários": all_users}
