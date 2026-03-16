import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.admin import admin_router
from app.api.links import links_router, redirect_router
from app.auth.router import router as auth_router
from app.database import Base, engine

app = FastAPI()


# if os.getenv("LOCAL_DEV") == "1":
Base.metadata.create_all(bind=engine)


app.include_router(links_router)
app.include_router(auth_router)
app.include_router(redirect_router)
app.include_router(admin_router)


app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def frontend():
    return FileResponse("frontend/index.html")
