from fastapi import APIRouter, UploadFile, Depends
from app.deps.auth import get_current_user
from app.ai.vision.image_pipeline import ImageIngestionService

router = APIRouter(prefix="/vision", tags=["Vision"])


@router.post("/upload")
async def upload_image(
    file: UploadFile,
    user=Depends(get_current_user),
):
    image_bytes = await file.read()

    description = await ImageIngestionService.ingest(
        image_bytes=image_bytes,
        user_id=user.id,
    )

    return {
        "description": description,
        "message": "Image processed and stored for future conversations.",
    }
