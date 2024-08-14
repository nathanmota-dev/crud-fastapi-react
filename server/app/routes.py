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
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from . import models
from .database import get_db
from evtx import PyEvtxParser
import matplotlib.pyplot as plt
from typing import List
from datetime import datetime
import pytz
import xml.etree.ElementTree as ET

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/forms")
def read_upload(db: Session = Depends(get_db)):
    all_forms = db.query(models.FileRecord).all()
    return {"Todos Formulários de Contato": all_forms}


def get_filename(file):
    objeto_evtx = PyEvtxParser(io.BytesIO(file))
    for registro in objeto_evtx.records():
        match = re.search(r"<Channel>(.*?)</Channel>", registro["data"])
        if match:
            return match.group(1)
    return None  # Retorna None se não encontrar o filename


# PAREI NO 6,
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
            filename = get_filename(file_content)
            file_record = models.FileRecord(
                original_filename=filename,
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
    caminho_para_diretorio_atual = os.getcwd()
    print(caminho_para_diretorio_atual)
    caminho_para_csv = caminho_para_diretorio_atual + "\\assets"
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

            for registro in objeto_evtx.records():
                event_level_match = re.search(r"<Level>(.*?)</Level>", registro["data"])
                if not event_level_match:
                    continue
                event_level = event_level_match.group(1)
                if (
                    "Application" in arquivo.original_filename and event_level == "2"
                ) or (
                    "System" in arquivo.original_filename and event_level in ("1", "2")
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
            "filtered_records_com_falha": filtered_records_com_falha,
            "filtered_sem_falha": filtered_sem_falha,
            "registros_com_falha": registros_com_falha,
        }
    )


@router.post("/download6013", response_class=JSONResponse)
async def download6013(user_id: int = Query(...), db: Session = Depends(get_db)):
    user_record = (
        db.query(models.UserRecord).filter(models.UserRecord.id == user_id).first()
    )
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    registros = []
    for arquivo in user_record.files:
        try:
            file_content = arquivo.file
            objeto_evtx = PyEvtxParser(io.BytesIO(file_content))

            for registro in objeto_evtx.records():
                registros.append(registro)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao processar o arquivo EVTX: {str(e)}"
            )

    timezone_especifico = pytz.timezone("America/Sao_Paulo")

    registro_6013 = None
    for record in registros:
        # Parse o XML do registro
        event_element = ET.fromstring(record["data"])

        # Verifica se o registro contém o EventID 6013
        event_id_element = event_element.find(
            ".//ns0:EventID",
            namespaces={"ns0": event_element.tag.split("}")[0].strip("{")},
        )
        if (
            event_id_element is not None
            and event_id_element.text == "6013"
        ):
            # Busca o campo de TimeCreated
            event_time_created_element = event_element.find(
                ".//ns0:TimeCreated",
                namespaces={"ns0": event_element.tag.split("}")[0].strip("{")},
            )
            if event_time_created_element is not None:
                timestamp_str = event_time_created_element.attrib.get("SystemTime")
                if timestamp_str:
                    # Converte o horário de UTC para o fuso horário de Brasília
                    timestamp_utc = datetime.strptime(
                        timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).replace(tzinfo=pytz.UTC)

                    timestamp_manipulada = timestamp_utc.astimezone(timezone_especifico)
                    timestamp_manipulada_str = timestamp_manipulada.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                    # Atualiza o atributo SystemTime com o novo horário ajustado
                    event_time_created_element.set("SystemTime", timestamp_manipulada_str)

                    # Atualiza o registro 6013 com o novo XML
                    registro_6013 = ET.tostring(event_element, encoding="unicode")
                    break

    if registro_6013:
        # Salva o registro 6013 em um arquivo XML
        root = ET.Element("Events")
        event_element = ET.fromstring(registro_6013)
        root.append(event_element)

        tree = ET.ElementTree(root)
        tree.write(
            "registro_6013_modificado.xml", encoding="utf-8", xml_declaration=True
        )

        return JSONResponse(
            content={
                "detail": "Registro 6013 modificado salvo em registro_6013_modificado.xml"
            }
        )
    else:
        raise HTTPException(status_code=404, detail="Registro 6013 não encontrado")
    

# uvicorn app.main:app --reload --root-path server

# Vá para a aba "Headers".
# Adicione um novo cabeçalho: Content-Type com o valor multipart/form-data.
# Vá para a aba "Body".
# Selecione a opção "form-data".
# Adicione os campos do formulário: name, email e files:
# -Para name e email, defina o tipo como "Text" e insira os valores apropriados.
# -Para files, defina o tipo como "File". Clique em "Select Files" e escolha os arquivos que deseja enviar.
#     Repita este passo para cada arquivo que deseja enviar.
