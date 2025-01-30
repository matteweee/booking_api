import shutil

from fastapi import APIRouter, UploadFile

from app.tasks.tasks import process_pic

router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


@router.post("/upload/hotels")
async def upload_hotel_image(
    name: int,
    file: UploadFile,
):
    img_path = f"app/static/images/{name}.webp"
    with open(img_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    process_pic.delay(img_path)
