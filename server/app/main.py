from collections import defaultdict
import re
from typing import List
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from . import models
from .database import engine, get_db
from evtx import PyEvtxParser
import matplotlib.pyplot as plt
import io
import os
import pandas as pd
import xmltodict
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
        user_record = models.UserRecord(name=name, email=email)
        db.add(user_record)
        db.commit()
        db.refresh(user_record)  # Atualize para garantir que o ID está disponível

        for file in files:
            file_content = await file.read()
            file_record = models.FileRecord(
                original_filename=file.filename,
                file=file_content,
                user_id=user_record.id
            )
            db.add(file_record)

        db.commit()
        return {"detail": "Files uploaded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# "Params" no  postman, 'user_id'
@app.post("/download", response_class=JSONResponse)
async def download_file(user_id: int = Query(...), db: Session = Depends(get_db)):
    user_record = db.query(models.UserRecord).filter(models.UserRecord.id == user_id).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    registros_com_erro = []
    filtered_records_com_erro = []
    filtered_sem_erro = []

    caminho_para_csv = r"C:\Users\fdisu\OneDrive\Área de Trabalho\crud-fastapi-react\server\app"
    df_non_failure_events = pd.read_csv(os.path.join(caminho_para_csv, "1_non_failure_events.csv"), encoding='utf-8-sig', engine='python')

    dict_non_failure_events = defaultdict(list)
    for k, v in zip(df_non_failure_events.SourceName, df_non_failure_events.EventID):
        dict_non_failure_events[k.lower()].append(v)
    print("Non-failure events dictionary:", dict_non_failure_events)  # Verificar o dicionário de eventos não falhos
    
    for arquivo in user_record.files:
        try:
            file_content = arquivo.file
            print("File content length:", len(file_content))  # Verificar o tamanho do arquivo

            objeto_evtx = PyEvtxParser(io.BytesIO(file_content))
            total_records = sum(1 for _ in objeto_evtx.records_json())
            print("Total records:", total_records)  # Verificar o número total de registros

            objeto_evtx = PyEvtxParser(io.BytesIO(file_content))  # Reiniciar o parser
            record_count = 0

            for registro in objeto_evtx.records_json():
                record_count += 1
                if record_count % 1000 == 0:
                    print(f"Processing record {record_count} of {total_records}")

                event_level_match = re.search(r'<Level>(.*?)</Level>', registro['data'])
                if not event_level_match:
                    continue
                event_level = event_level_match.group(1)
                if ("Application" in arquivo.original_filename and event_level == "2") or \
                        ("System" in arquivo.original_filename and event_level in ("1", "2")):
                    registros_com_erro.append(registro)
            print("Number of error records:", len(registros_com_erro))  # Verificar o número de registros com erro

            for registro in registros_com_erro:
                line_filtered_1 = re.sub(r'<\?xml([\s\S]*?)>\n', '', registro['data'])
                line_filtered_2 = re.sub(r' xmlns=\"([\s\S]*?)\"', '', line_filtered_1)
                evento_estrutura_dict = xmltodict.parse(line_filtered_2)
                evento_estrutura_dict__tag_System = evento_estrutura_dict.get("Event").get("System")

                SourceName = evento_estrutura_dict__tag_System.get("Provider").get("@Name")
                if SourceName is None:
                    SourceName = evento_estrutura_dict__tag_System.get("Provider").get("@EventSourceName")

                EventID = evento_estrutura_dict__tag_System.get("EventID")

                if SourceName is not None:
                    print("SourceName:", SourceName)  # Verificar o SourceName
                else:
                    print("SourceName is None")

                print("EventID:", EventID)  # Verificar o EventID

                if SourceName.lower() in dict_non_failure_events:
                    listaDe_EventIDs = dict_non_failure_events[SourceName.lower()]
                    if int(EventID) in listaDe_EventIDs:
                        filtered_sem_erro.append(registro)
                        continue
                filtered_records_com_erro.append(registro)

            print("Filtered error records:", len(filtered_records_com_erro))  # Verificar o número de registros com erro filtrados
            print("Filtered non-error records:", len(filtered_sem_erro))  # Verificar o número de registros sem erro filtrados

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o arquivo EVTX: {str(e)}"
            )

    return JSONResponse(content={
        "detail": f"registros com erro: {len(filtered_records_com_erro)}\n registros sem erro: {len(filtered_sem_erro)}",
        "registros_com_erro": filtered_records_com_erro,
        "registros_sem_erro": filtered_sem_erro
    })
    
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
