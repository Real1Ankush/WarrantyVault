from sqlalchemy.orm import Session

from backend.app.models.document import Document


class DocumentRepository:

    def create_document(
        self,
        db: Session,
        asset_id: int,
        document_type: str,
        original_filename: str,
        file_path: str,
        mime_type: str | None = None,
    ) -> Document:

        document = Document(
            asset_id=asset_id,
            document_type=document_type,
            original_filename=original_filename,
            file_path=file_path,
            mime_type=mime_type,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def get_documents_for_asset(
        self,
        db: Session,
        asset_id: int,
    ):
        return (
            db.query(Document)
            .filter(Document.asset_id == asset_id)
            .all()
        )

    def get_document(
        self,
        db: Session,
        asset_id: int,
        document_type: str,
    ):
        return (
            db.query(Document)
            .filter(
                Document.asset_id == asset_id,
                Document.document_type == document_type,
            )
            .first()
        )