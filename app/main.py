from fastapi import FastAPI

from app.routes import router

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

app = FastAPI()

app.include_router(router)