from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import distros, recommend

app = FastAPI(
    title="I Can Run Linux API",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(distros.router)
app.include_router(recommend.router)
