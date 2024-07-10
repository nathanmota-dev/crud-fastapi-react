# NA PASTAR SERVER, E NÃO NA APP.
# uvicorn app.main:app --reload --root-path server

# Vá para a aba "Headers".
# Adicione um novo cabeçalho: Content-Type com o valor multipart/form-data.
# Vá para a aba "Body".
# Selecione a opção "form-data".
# Adicione os campos do formulário: name, email e files:
# -Para name e email, defina o tipo como "Text" e insira os valores apropriados.
# -Para files, defina o tipo como "File". Clique em "Select Files" e escolha os arquivos que deseja enviar. 
#     Repita este passo para cada arquivo que deseja enviar.


from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Form,
    Query,
    Response,
)
from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from . import models
from .database import engine, get_db
from .models import FileRecordResponse  # Importa o modelo Pydantic para a resposta
from evtx import PyEvtxParser
import tempfile
import matplotlib.pyplot as plt
import io
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
async def upload_files(
    name: str = Form(...),
    email: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    try:
        for file in files:
            file_content = await file.read()
            file_record = models.FileRecord(
                name=name,
                email=email,
                original_filename=file.filename,
                file=file_content,
            )
            db.add(file_record)
        db.commit()
        return {"detail": "Files uploaded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/files", response_model=List[FileRecordResponse])
# def list_files(db: Session = Depends(get_db)):
#     files = db.query(models.FileRecord).all() # Retorna todos os registros da tabela 'file_records'
#     return files

# "Params" no  postman, 'file_id' 
@app.post("/download", response_class=JSONResponse)
async def download_file(file_id: int = Query(...), db: Session = Depends(get_db)):
    file_record = db.query(models.FileRecord).filter(models.FileRecord.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_record.file)
        temp_file_path = temp_file.name

    try:
        parser = PyEvtxParser(temp_file_path)
        records = [record for record in parser.records_json()]
        return JSONResponse(content=records)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o arquivo EVTX: {str(e)}"
        )
    finally:
        os.remove(temp_file_path)


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

    with open(file_path, "rb") as f:
        file_content = f.read()

    return {
        "message": "File saved successfully",
        "file_path": file_path,
        "file_content": file_content,
    }


@app.get("/plot")
async def get_plot():
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]

    plt.figure()
    plt.plot(x, y)
    plt.title("Gráfico teste")
    plt.xlabel("X")
    plt.ylabel("Y")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")
