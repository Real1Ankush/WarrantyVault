from backend.app.services.document_repository import (
    DocumentRepository,
)


class ClaimService:

    def __init__(self):
        self.document_repository = DocumentRepository()

    def prepare_claim(
        self,
        db,
        asset,
    ):
        documents = (
            self.document_repository
            .get_documents_for_asset(
                db,
                asset.id,
            )
        )

        receipt = None
        warranty_document = None

        for document in documents:

            if document.document_type == "receipt":
                receipt = document

            elif document.document_type == "warranty":
                warranty_document = document

        # --------------------------------------------------
        # WARRANTY STATUS
        # --------------------------------------------------

        if asset.warranty_status == "active":

            claim_state = "potentially_eligible"

            warranty_message = (
                "The stored warranty information indicates "
                "that the warranty is currently active."
            )

        elif asset.warranty_status == "expired":

            claim_state = "warranty_expired"

            warranty_message = (
                "The stored warranty information indicates "
                "that the warranty has expired."
            )

        else:

            claim_state = "warranty_unknown"

            warranty_message = (
                "No verified warranty status is available "
                "for this product."
            )

        # --------------------------------------------------
        # DOCUMENTS
        # --------------------------------------------------

        document_list = []

        if receipt is not None:

            document_list.append(
                {
                    "type": "receipt",
                    "status": "available",
                    "document_id": receipt.id,
                    "filename": receipt.original_filename,
                    "endpoint": (
                        f"/api/assets/"
                        f"{asset.id}/documents/receipt"
                    ),
                }
            )

        else:

            document_list.append(
                {
                    "type": "receipt",
                    "status": "missing",
                }
            )

        if warranty_document is not None:

            document_list.append(
                {
                    "type": "warranty",
                    "status": "available",
                    "document_id": warranty_document.id,
                    "filename": (
                        warranty_document.original_filename
                    ),
                    "endpoint": (
                        f"/api/assets/"
                        f"{asset.id}/documents/warranty"
                    ),
                }
            )

        # --------------------------------------------------
        # CLAIM SUMMARY
        # --------------------------------------------------

        return {
            "claim_state": claim_state,

            "product": {
                "name": asset.product,
                "product_id": asset.product_id,
                "seller": asset.seller,
            },

            "purchase": {
                "purchase_date": (
                    asset.purchase_date.isoformat()
                    if asset.purchase_date
                    else None
                ),
                "invoice_number": asset.invoice_number,
                "order_number": asset.order_number,
                "amount": asset.total_amount,
            },

            "warranty": {
                "status": asset.warranty_status,
                "months": asset.warranty_months,
                "expiry": (
                    asset.warranty_expiry.isoformat()
                    if asset.warranty_expiry
                    else None
                ),
                "source": asset.warranty_source,
                "message": warranty_message,
            },

            "documents": document_list,

            "next_steps": self.build_next_steps(
                asset,
                receipt,
                warranty_document,
            ),
        }

    @staticmethod
    def build_next_steps(
        asset,
        receipt,
        warranty_document,
    ):

        steps = []

        if asset.warranty_status == "active":

            steps.append(
                "Keep the purchase invoice ready."
            )

            if warranty_document is not None:

                steps.append(
                    "Keep the warranty document ready."
                )

            steps.append(
                "Contact the manufacturer's "
                "authorized service/support channel."
            )

            steps.append(
                "The final warranty decision remains "
                "with the manufacturer or authorized "
                "service provider."
            )

        elif asset.warranty_status == "expired":

            steps.append(
                "The stored warranty information indicates "
                "that the warranty has expired."
            )

            steps.append(
                "Check whether another coverage such as "
                "insurance or an extended warranty exists."
            )

        else:

            steps.append(
                "Find or upload a warranty document "
                "before relying on warranty coverage."
            )

            steps.append(
                "The purchase invoice is still available "
                "as proof of purchase."
            )

        if receipt is None:

            steps.append(
                "No receipt document is currently linked "
                "to this asset."
            )

        return steps