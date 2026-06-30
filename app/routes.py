from fastapi import APIRouter

from app.metadata import get_metadata

router = APIRouter()


@router.get("/")
def home():
    return get_metadata()