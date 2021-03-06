# uvicorn app.main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, item, basket, address

app = FastAPI()
origins = ["*"]
app.include_router(user.router)
app.include_router(item.router)
app.include_router(basket.router)
app.include_router(address.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "e-commerce api V0.0.1!"}
