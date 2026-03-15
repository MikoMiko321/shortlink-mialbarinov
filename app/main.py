from fastapi import FastAPI

from app.api.links import router
from app.database import Base, engine

app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(router)


@app.get("/")
def root():
    return {"service": "shortlink"}
