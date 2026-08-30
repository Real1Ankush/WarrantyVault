from pathlib import Path
import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.vision_service import (
    VisionService,
    VisionExtractionError,
)

router = APIRouter(
    prefix="/api/receipts",
    tags=["Receipts"],
)

def get_upload_dir() -> Path:
    upload_dir = Path(os.getenv("UPLOAD_DIR", "backend/uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
}

vision_service = VisionService()


@router.post("/upload")
async def upload_receipt(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    file_extension = (
        Path(file.filename)
        .suffix
        .lower()
    )

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Upload JPG, JPEG, PNG or PDF."
            ),
        )

    file_path = (
        get_upload_dir()
        / f"receipt_{uuid4().hex}_{Path(file.filename).name}"
    )

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        if file_extension == ".pdf":
            raise HTTPException(
                status_code=400,
                detail=(
                    "PDF receipt extraction is not "
                    "supported by the vision pipeline yet."
                ),
            )

        receipt_data = (
            vision_service.extract_receipt(
                str(file_path)
            )
        )

        if (
            receipt_data.get("product") is None
            and receipt_data.get("invoice_number") is None
            and receipt_data.get("total_amount") is None
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Could not reliably extract receipt information. "
                    "Please upload a clearer receipt image."
                ),
            )

        return {
            "message": (
                "Receipt uploaded and "
                "processed successfully"
            ),
            "filename": file.filename,
            "file_type": file_extension,
            "file_path": str(file_path),
            "receipt": receipt_data,
        }

    except VisionExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Receipt processing failed: "
                f"{exc}"
            ),
        ) from exc

    finally:
        await file.close()
