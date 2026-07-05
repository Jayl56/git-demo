import boto3
from pathlib import Path
import uuid
import datetime
from fastapi import HTTPException, UploadFile
from config import S3_BUCKET_NAME
from typing import BinaryIO

client=boto3.client("s3")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def get_file_size(file: BinaryIO) -> int:
    current = file.tell()
    file.seek(0, 2)
    size = file.tell()
    file.seek(current)
    return size

def extract_metadata(file: UploadFile)->dict:
    return {
        "filename": file.filename,
        "extension": Path(file.filename).suffix.lower().lstrip("."),
        "size": get_file_size(file.file),
        "upload_date": datetime.utcnow()
    }

def validate_image(file: UploadFile) -> None:
    extension = Path(file.filename).suffix.lower()
    jpeg_signature = b"\xff\xd8\xff"
    png_signature = b"\x89PNG\r\n\x1a\n"

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG images are allowed."
        )

    header = file.read(8)
    file.seek(0)

    # JPEG (.jpg y .jpeg)
    if extension in (".jpg", ".jpeg"):
        if not header.startswith(jpeg_signature):
            raise HTTPException(
                status_code=400,
                detail="Invalid JPEG image."
            )

    # PNG
    elif extension == ".png":
        if header != png_signature:
            raise HTTPException(
                status_code=400,
                detail="Invalid PNG image."
            )

def upload_s3_file_object(file: UploadFile)->str:
     validate_image(file)
     key= f"{uuid.uuid4()}_{file.filename}"
     client.upload_fileobj(
        file.file,
        S3_BUCKET_NAME,
        key)
     file.file.seek(0)
     return key

def get_s3_doc_url_download(key:str)->str:
    url=client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': S3_BUCKET_NAME,
            'Key': key
        },
        ExpiresIn=3600
    )
    return url

def delete_s3_file_object(
    key: str
) -> None:
    client.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=key
    )



