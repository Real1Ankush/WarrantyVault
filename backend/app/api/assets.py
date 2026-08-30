from pathlib import Path
import os
import shutil
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from backend.app.database import get_db

from backend.app.services.asset_repository import (
    AssetRepository,
)

from backend.app.services.asset_service import (
    AssetService,
)

from backend.app.services.document_repository import (
    DocumentRepository,
)

from backend.app.services.ocr_service import (
    OCRService,
)

from backend.app.services.vision_service import (
    VisionService,
)

from backend.app.services.warranty_extractor import (
    WarrantyExtractor,
)


router = APIRouter(
    prefix="/api/assets",
    tags=["Assets"],
)


def get_upload_dir() -> Path:
    upload_dir = Path(os.getenv("UPLOAD_DIR", "backend/uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


ocr_service = OCRService()

vision_service = VisionService()

warranty_extractor = WarrantyExtractor()

asset_service = AssetService()

asset_repository = AssetRepository()

document_repository = DocumentRepository()


# =========================================================
# PROCESS ASSET
# =========================================================

@router.post("/process")
async def process_asset(
    receipt: UploadFile = File(...),
    warranty: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):

    upload_dir = get_upload_dir()
    receipt_path = (
        upload_dir
        / f"receipt_{uuid4().hex}_{Path(receipt.filename).name}"
    )

    warranty_path = None
    keep_files = False

    try:

        # -------------------------------------------------
        # SAVE RECEIPT
        # -------------------------------------------------

        with receipt_path.open(
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                receipt.file,
                buffer,
            )

        # -------------------------------------------------
        # RECEIPT EXTRACTION
        # -------------------------------------------------

        receipt_data = (
            vision_service.extract_receipt(
                str(receipt_path)
            )
        )

        # -------------------------------------------------
        # WARRANTY
        # -------------------------------------------------

        warranty_data = {
            "warranty_months": None
        }

        if warranty is not None:

            warranty_path = (
                upload_dir
                / f"warranty_{uuid4().hex}_{Path(warranty.filename).name}"
            )

            with warranty_path.open(
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    warranty.file,
                    buffer,
                )

            warranty_ocr = (
                ocr_service.extract_text(
                    str(warranty_path)
                )
            )

            warranty_data = (
                warranty_extractor.extract(
                    warranty_ocr
                )
            )

        # -------------------------------------------------
        # BUILD ASSET
        # -------------------------------------------------

        asset_data = (
            asset_service.build_asset_record(
                receipt=receipt_data,
                warranty=warranty_data,
            )
        )

        # -------------------------------------------------
        # CHECK FOR DUPLICATE
        # -------------------------------------------------

        existing_asset = asset_repository.find_duplicate(
            db,
            asset_data,
        )

        if existing_asset is not None:

            return {
                "message": (
                    "This purchase is already in your wallet."
                ),
                "already_exists": True,
                "asset_id": existing_asset.id,
                "asset": serialize_asset(
                    existing_asset
                ),
            }

        # -------------------------------------------------
        # SAVE NEW ASSET
        # -------------------------------------------------

        saved_asset = (
            asset_repository.create_asset(
                db,
                asset_data,
            )
        )

        # -------------------------------------------------
        # SAVE RECEIPT DOCUMENT
        # -------------------------------------------------

        receipt_document = (
            document_repository.create_document(
                db=db,
                asset_id=saved_asset.id,
                document_type="receipt",
                original_filename=receipt.filename,
                file_path=str(receipt_path),
                mime_type=receipt.content_type,
            )
        )

        # -------------------------------------------------
        # SAVE WARRANTY DOCUMENT
        # -------------------------------------------------

        warranty_document = None

        if (
            warranty is not None
            and warranty_path is not None
        ):

            warranty_document = (
                document_repository.create_document(
                    db=db,
                    asset_id=saved_asset.id,
                    document_type="warranty",
                    original_filename=warranty.filename,
                    file_path=str(warranty_path),
                    mime_type=warranty.content_type,
                )
            )

        documents = [
            {
                "id": receipt_document.id,
                "type": (
                    receipt_document.document_type
                ),
                "filename": (
                    receipt_document.original_filename
                ),
            }
        ]

        if warranty_document is not None:

            documents.append(
                {
                    "id": warranty_document.id,
                    "type": (
                        warranty_document.document_type
                    ),
                    "filename": (
                        warranty_document.original_filename
                    ),
                }
            )

        keep_files = True

        return {
            "message": (
                "Asset processed and saved successfully"
            ),
            "asset_id": saved_asset.id,
            "asset": asset_data,
            "documents": documents,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Asset processing failed: "
                f"{exc}"
            ),
        )

    finally:

        await receipt.close()

        if warranty is not None:
            await warranty.close()

        if not keep_files:
            receipt_path.unlink(missing_ok=True)

            if warranty_path is not None:
                warranty_path.unlink(missing_ok=True)


# =========================================================
# SEARCH
# =========================================================

@router.get("/search")
def search_assets(
    q: str = Query(
        ...,
        min_length=1,
    ),
    db: Session = Depends(get_db),
):

    assets = (
        asset_repository.search_assets(
            db,
            q,
        )
    )

    return {
        "query": q,
        "count": len(assets),
        "assets": [
            serialize_asset(asset)
            for asset in assets
        ],
    }


# =========================================================
# GET ALL
# =========================================================

@router.get("/")
def get_assets(
    db: Session = Depends(get_db),
):

    assets = (
        asset_repository.get_all_assets(
            db
        )
    )

    return {
        "count": len(assets),
        "assets": [
            serialize_asset(asset)
            for asset in assets
        ],
    }


# =========================================================
# GET DOCUMENTS
# =========================================================

@router.get(
    "/{asset_id}/documents"
)
def get_asset_documents(
    asset_id: int,
    db: Session = Depends(get_db),
):

    documents = (
        document_repository
        .get_documents_for_asset(
            db,
            asset_id,
        )
    )

    return {
        "asset_id": asset_id,
        "count": len(documents),
        "documents": [
            {
                "id": document.id,
                "type": (
                    document.document_type
                ),
                "filename": (
                    document.original_filename
                ),
                "file_path": (
                    document.file_path
                ),
                "mime_type": (
                    document.mime_type
                ),
                "uploaded_at": (
                    document.uploaded_at
                    .isoformat()
                ),
            }
            for document in documents
        ],
    }


# =========================================================
# GET ACTUAL DOCUMENT
# =========================================================

@router.get(
    "/{asset_id}/documents/{document_type}"
)
def get_asset_document(
    asset_id: int,
    document_type: str,
    db: Session = Depends(get_db),
):

    document = (
        document_repository.get_document(
            db,
            asset_id,
            document_type,
        )
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(
        document.file_path
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Stored document file "
                "no longer exists"
            ),
        )

    return FileResponse(
        path=file_path,
        media_type=(
            document.mime_type
            or "application/octet-stream"
        ),
        filename=(
            document.original_filename
        ),
    )


# =========================================================
# DELETE ASSET
# =========================================================

@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = asset_repository.get_asset_by_id(
        db,
        asset_id,
    )

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    try:
        # -------------------------------------------------
        # DELETE LINKED DOCUMENT FILES
        # -------------------------------------------------

        documents = (
            document_repository
            .get_documents_for_asset(
                db,
                asset_id,
            )
        )

        for document in documents:

            file_path = Path(
                document.file_path
            )

            if file_path.exists():
                file_path.unlink()

        # -------------------------------------------------
        # DELETE DOCUMENT DATABASE ROWS
        # -------------------------------------------------

        for document in documents:
            db.delete(document)

        # -------------------------------------------------
        # DELETE ASSET
        # -------------------------------------------------

        db.delete(asset)

        db.commit()

        return {
            "message": "Asset deleted successfully",
            "asset_id": asset_id,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete asset: "
                f"{exc}"
            ),
        )


# =========================================================
# SERIALIZATION
# =========================================================

def serialize_asset(asset):

    return {
        "id": asset.id,

        "product": asset.product,

        "product_id": asset.product_id,

        "seller": asset.seller,

        "invoice_number": (
            asset.invoice_number
        ),

        "order_number": (
            asset.order_number
        ),

        "order_date": (
            asset.order_date.isoformat()
            if asset.order_date
            else None
        ),

        "invoice_date": (
            asset.invoice_date.isoformat()
            if asset.invoice_date
            else None
        ),

        "purchase_date": (
            asset.purchase_date.isoformat()
            if asset.purchase_date
            else None
        ),

        "total_amount": (
            asset.total_amount
        ),

        "warranty_months": (
            asset.warranty_months
        ),

        "warranty_source": (
            asset.warranty_source
        ),

        "warranty_expiry": (
            asset.warranty_expiry.isoformat()
            if asset.warranty_expiry
            else None
        ),

        "warranty_status": (
            asset.warranty_status
        ),
    }
