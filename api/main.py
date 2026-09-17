
from fastapi import FastAPI
from api.router.data import router

app = FastAPI()
app.include_router(router)