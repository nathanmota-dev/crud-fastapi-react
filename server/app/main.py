from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from . import models
from .database import engine, get_db
from evtx import PyEvtxParser
import tempfile

# Cria todas as tabelas do banco de dados
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
    db: Session = Depends(get_db),
):
    try:
        file_content = await file.read()
        form_create = models.FileRecord(name=name, email=email, file=file_content)
        db.add(form_create)
        db.commit()
        db.refresh(form_create)
        return {"Usuário Criado": "User create successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download", response_class=JSONResponse)
async def download_file(file_id: int = Query(...), db: Session = Depends(get_db)):
    file_record = db.query(models.FileRecord).filter(models.FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    # Cria um arquivo temporário para armazenar o conteúdo binário
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file_record.file)
    temp_file.close()

    # Extrai e converte o conteúdo do arquivo .evtx em JSON
    try:
        caminho_arquivo = PyEvtxParser(temp_file.name)
        records = [record for record in caminho_arquivo.records_json()]
        return JSONResponse(content=records)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo EVTX: {str(e)}")
    
    
@app.post("/save")
async def save_file(file_id: int = Form(...), db: Session = Depends(get_db)):
    file_record = (
        db.query(models.FileRecord).filter(models.FileRecord.id == file_id).first()
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = f"./saved_files/file_{file_id}.bin"
    with open(file_path, "wb") as f:
        f.write(file_record.file)

    # Leitura e extração de informações do arquivo
    with open(file_path, "rb") as f:
        file_content = f.read()

    return {
        "message": "File saved successfully",
        "file_path": file_path,
        "file_content": file_content,
    }
