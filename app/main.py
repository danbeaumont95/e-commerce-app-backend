# uvicorn app.main:app --reload
from fastapi import FastAPI

from .routers import user, item

app = FastAPI()

app.include_router(user.router)
app.include_router(item.router)


@app.get("/")
async def root():
    return {"message": "e-commerce api V0.0.1!"}
