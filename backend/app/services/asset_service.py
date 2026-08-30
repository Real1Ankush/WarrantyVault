from datetime import date

from backend.app.services.warranty_service import (
    WarrantyService,
)


class AssetService:

    def __init__(self):
        self.warranty_service = WarrantyService()

    def build_asset_record(
        self,
        receipt: dict,
        warranty: dict,
        today: date | None = None,
    ):

        purchase_date = receipt.get(
            "purchase_date"
        )

        warranty_months = warranty.get(
            "warranty_months"
        )

        result = {
            "product": receipt.get("product"),
            "product_id": receipt.get("product_id"),

            "seller": receipt.get("seller"),

            "invoice_number": receipt.get(
                "invoice_number"
            ),

            "order_number": receipt.get(
                "order_number"
            ),

            # Preserve both original dates.
            "order_date": receipt.get(
                "order_date"
            ),

            "invoice_date": receipt.get(
                "invoice_date"
            ),

            # Business date used for warranty
            # calculations.
            "purchase_date": purchase_date,

            "total_amount": receipt.get(
                "total_amount"
            ),

            "warranty_months": warranty_months,

            "warranty_source": (
                "warranty_document"
                if warranty_months is not None
                else None
            ),

            "warranty_expiry": None,

            "warranty_status": "unknown",
        }

        # Only calculate warranty when both
        # purchase date and verified duration exist.
        if (
            purchase_date
            and warranty_months is not None
        ):

            warranty_result = (
                self.warranty_service.get_status(
                    purchase_date=purchase_date,
                    warranty_months=warranty_months,
                    today=today,
                )
            )

            result["warranty_expiry"] = (
                warranty_result[
                    "warranty_expiry"
                ]
            )

            result["warranty_status"] = (
                warranty_result["status"]
            )

        return result