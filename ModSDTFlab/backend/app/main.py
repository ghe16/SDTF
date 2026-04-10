from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, algorithms, executions

# Import core to register engines
from app import core

app = FastAPI(title="SDTFLab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(algorithms.router, prefix="/api")
app.include_router(executions.router, prefix="/api")