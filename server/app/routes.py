from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Form,
    Query,
    Response,
)
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List
from collections import defaultdict
import io
import os
import re
import xmltodict
import pandas as pd
import matplotlib.pyplot as plt
from . import models
from .database import get_db, connect_to_db
from evtx import PyEvtxParser

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/forms")
def read_upload(db: Session = Depends(get_db)):
    all_forms = db.query(models.FileRecord).all()
    return {"Todos Formulários de Contato": all_forms}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
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


@router.post("/download", response_class=JSONResponse)
async def download_file(file_id: int = Query(...), db: Session = Depends(get_db)):
    # Recupera o registro do banco de dados
    file_record = (
        db.query(models.FileRecord).filter(models.FileRecord.id == file_id).first()
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_content = io.BytesIO(file_record.file)
        parser = PyEvtxParser(file_content)
        error_records = []

        # Filtra registros de erro
        for record in parser.records_json():
            event_level_match = re.search(r"<Level>(.*?)</Level>", record["data"])
            if not event_level_match:
                continue
            event_level = event_level_match.group(1)
            if (
                "Application" in file_record.original_filename and event_level == "2"
            ) or (
                "System" in file_record.original_filename and event_level in ("1", "2")
            ):
                error_records.append(record)

        # Carrega eventos não-falhos
        caminho_para_csv = r"C:\Users\natha\Desktop\git\crud-fastapi-react\server\app\assets"
        df_non_failure_events = pd.read_csv(
            os.path.join(caminho_para_csv, "1_non_failure_events.csv"),
            encoding="utf-8-sig",
            engine="python",
        )

        dict_non_failure_events = defaultdict(list)
        for k, v in zip(
            df_non_failure_events.SourceName, df_non_failure_events.EventID
        ):
            dict_non_failure_events[k.lower()].append(v)

        # Filtra registros de não falhos
        filtered_records = []
        for record in error_records:
            line_filtered_1 = re.sub(r"<\?xml([\s\S]*?)>\n", "", record["data"])
            line_filtered_2 = re.sub(r" xmlns=\"([\s\S]*?)\"", "", line_filtered_1)
            evento_estrutura_dict = xmltodict.parse(line_filtered_2)
            evento_estrutura_dict__tag_System = evento_estrutura_dict.get("Event").get(
                "System"
            )

            SourceName = evento_estrutura_dict__tag_System.get("Provider").get("@Name")
            if SourceName is None:
                SourceName = evento_estrutura_dict__tag_System.get("Provider").get(
                    "@EventSourceName"
                )

            EventID = evento_estrutura_dict__tag_System.get("EventID")
            if isinstance(EventID, dict):
                EventID = EventID.get("#text")

            if SourceName.lower() in dict_non_failure_events:
                listaDe_EventIDs = dict_non_failure_events[SourceName.lower()]
                if int(EventID) in listaDe_EventIDs:
                    continue
            filtered_records.append(record)

        return JSONResponse(content=filtered_records)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar o arquivo EVTX: {str(e)}"
        )


@router.post("/save")
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


@router.get("/plot")
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
