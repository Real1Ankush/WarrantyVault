from backend.app.database import SessionLocal
from backend.app.models.asset import Asset
from backend.app.models.document import Document
from backend.app.services.document_repository import DocumentRepository


db = SessionLocal()

repository = DocumentRepository()

try:
    document = repository.create_document(
        db=db,
        asset_id=2,
        document_type="receipt",
        original_filename="demo.jpg",
        file_path="backend/uploads/receipt_demo.jpg",
        mime_type="image/jpeg",
    )

    print("Document added successfully.")
    print(f"Document ID: {document.id}")
    print(f"Asset ID: {document.asset_id}")
    print(f"File: {document.file_path}")

finally:
    db.close()