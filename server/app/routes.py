from collections import defaultdict
import re
import io
import os
import pandas as pd
import xmltodict
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
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import models
from .database import get_db
from evtx import PyEvtxParser
import matplotlib.pyplot as plt
from typing import List
from .config import caminho_para_csv

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
        user_record = models.UserRecord(name=name, email=email)
        db.add(user_record)
        db.commit()
        db.refresh(user_record)

        for file in files:
            file_content = await file.read()
            file_record = models.FileRecord(
                original_filename=file.filename,
                file=file_content,
                user_id=user_record.id,
            )
            db.add(file_record)

        db.commit()
        return {"detail": "Files uploaded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download", response_class=JSONResponse)
async def download_file(user_id: int = Query(...), db: Session = Depends(get_db)):
    user_record = (
        db.query(models.UserRecord).filter(models.UserRecord.id == user_id).first()
    )
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    registros_com_falha = []
    filtered_records_com_falha = []
    filtered_sem_falha = []

    df_non_failure_events = pd.read_csv(
        os.path.join(caminho_para_csv, "1_non_failure_events.csv"),
        encoding="utf-8-sig",
        engine="python",
    )

    dict_non_failure_events = defaultdict(list)
    for k, v in zip(df_non_failure_events.SourceName, df_non_failure_events.EventID):
        dict_non_failure_events[k.lower()].append(v)

    for arquivo in user_record.files:
        try:
            file_content = arquivo.file

            objeto_evtx = PyEvtxParser(io.BytesIO(file_content))
            total_records = sum(1 for _ in objeto_evtx.records())

            objeto_evtx = PyEvtxParser(io.BytesIO(file_content))
            record_count = 0

            for registro in objeto_evtx.records():
                record_count += 1

                event_level_match = re.search(r"<Level>(.*?)</Level>", registro["data"])
                if not event_level_match:
                    continue
                event_level = event_level_match.group(1)
                if (
                    "Application.evtx" in arquivo.original_filename
                    and event_level == "2"
                ) or (
                    "System.evtx" in arquivo.original_filename
                    and event_level in ("1", "2")
                ):
                    registros_com_falha.append(registro)

            for registro in registros_com_falha:
                line_filtered_1 = re.sub(r"<\?xml([\s\S]*?)>\n", "", registro["data"])
                line_filtered_2 = re.sub(r" xmlns=\"([\s\S]*?)\"", "", line_filtered_1)
                evento_estrutura_dict = xmltodict.parse(line_filtered_2)
                evento_estrutura_dict__tag_System = evento_estrutura_dict.get(
                    "Event"
                ).get("System")

                SourceName = evento_estrutura_dict__tag_System.get("Provider").get(
                    "@Name"
                )
                if SourceName is None:
                    SourceName = evento_estrutura_dict__tag_System.get("Provider").get(
                        "@EventSourceName"
                    )

                EventID = evento_estrutura_dict__tag_System.get("EventID")

                if isinstance(EventID, dict):
                    EventID = EventID.get("#text", "")

                if SourceName.lower() in dict_non_failure_events:
                    listaDe_EventIDs = dict_non_failure_events[SourceName.lower()]
                    if int(EventID) in listaDe_EventIDs:
                        filtered_sem_falha.append(registro)
                        continue
                filtered_records_com_falha.append(registro)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o arquivo EVTX: {str(e)}"
            )

    return JSONResponse(
        content={
            "detail": f"registros com falha: {len(filtered_records_com_falha)} \n registros sem erro: {len(filtered_sem_falha)}",
            "registros_com_falha": filtered_records_com_falha,
            "registros_sem_falha": filtered_sem_falha,
        }
    )


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