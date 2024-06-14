from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/upload")
async def upload_file(
    name: str = Form(...), 
    email: str = Form(...), 
    file: UploadFile = File(...)
):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    return JSONResponse(
        content={"name": name, "email": email, "file_path": file_location}
    )
