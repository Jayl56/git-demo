from fastapi import APIRouter,UploadFile,HTTPException,File
from fastapi.encoders import jsonable_encoder
from db import get_connection
import s3_amazon as s3
from app.metadata import get_metadata_region

router = APIRouter()


@router.get("/")
def home():
    return get_metadata_region()

@router.post("/image",status_code=201)
def upload_image(file:UploadFile= File(...))->dict:
    key=s3.upload_s3_file_object(file)
    metadata=s3.extract_metadata(file)
    conn = get_connection()
    try:
     with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO images
            (filename, s3_key, extension, size, upload_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (metadata["filename"], key, metadata["extension"], metadata["size"], metadata["upload_date"])
        )
        conn.commit()
    finally:
        conn.close()

    return {"message":"Image uploaded"}

@router.get("/download/{filename}",status_code=200)
def download_image(filename:str)->str:
    conn=get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT s3_key
            FROM images
            WHERE filename = %s;
            """,
            (filename,)
        )
        result = cursor.fetchone()
    conn.close()
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found."
        )

    url=s3.get_s3_doc_url_download(result["s3_key"])
    return url


@router.get("/metadata/{filename}",status_code=200)
def get_metadata_image(filename:str)->dict:
    conn=get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT filename, extension, size, upload_date
            FROM images
            WHERE filename=%s
            """,
            (filename,)
        )

        image = cursor.fetchone()
    conn.close()
    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found."
        )

    return jsonable_encoder(image)

@router.get("/random/",status_code=200)
def get_metadata_random()->dict:
    conn=get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                filename,
                extension,
                size,
                upload_date
            FROM images
            ORDER BY RAND()
            LIMIT 1;
            """
        )

        image = cursor.fetchone()
    conn.close()

    if image is None:
        raise HTTPException(
                status_code=404,
                detail="No images found."
            )
    return jsonable_encoder(image)

@router.delete("/image/{filename}",status_code=204)
def delete_image(filename:str)->None:
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT s3_key
            FROM images
            WHERE filename = %s;
            """,
            (filename,)
        )

        result = cursor.fetchone()

    if result is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="No images found."
        )

    key=result["s3_key"]
    s3.delete_s3_file_object(key)

    with conn.cursor() as cursor:
        cursor.execute("""
         DELETE FROM images
         WHERE filename = %s
        """,
            (filename,))

    conn.commit()
    conn.close()