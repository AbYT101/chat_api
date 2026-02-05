from fastapi import APIRouter, UploadFile, Depends
from app.deps.auth import get_current_user
from app.ai.vision.image_pipeline import ImageIngestionService

router = APIRouter(prefix="/vision", tags=["Vision"])


@router.post("/upload")
async def upload_image(
    file: UploadFile,
    user=Depends(get_current_user),
):
    """Upload image, process with vision AI, and store in vector database"""
    image_bytes = await file.read()

    description = await ImageIngestionService.ingest(
        image_bytes=image_bytes,
        user_id=user.id,
        filename=file.filename,
        content_type=file.content_type,
    )

    return {
        "description": description,
        "ingestion_type": "image",
        "source": file.filename,
        "message": "Image processed and stored in vector database.",
    }
