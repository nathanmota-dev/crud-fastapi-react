from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .database import connect_to_db, engine
from . import models
from dotenv import load_dotenv

load_dotenv()

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

app.include_router(router)


@app.on_event("startup")
async def startup():
    app.state.db = await connect_to_db()


@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()
