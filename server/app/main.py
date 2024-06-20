from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine, get_db

# Criar todas as tabelas do banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/forms")
def read_upload(db: Session = Depends(get_db)):
    all_forms = db.query(models.FileRecord).all()
    return {"Todos Formulários de Contato": all_forms}


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    name: str = Form(...), 
    email: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_content = await file.read()
        form_create = models.FileRecord(name=name, email=email, file=file_content)
        db.add(form_create)
        db.commit()
        db.refresh(form_create)
        return {"Usuário Criado": form_create}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
