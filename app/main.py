from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.links import router as links_router
from app.auth.router import router as auth_router
from app.database import Base, engine

app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(links_router)


app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def frontend():
    return FileResponse("frontend/index.html")
