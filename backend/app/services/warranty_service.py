from datetime import date
from dateutil.relativedelta import relativedelta


class WarrantyService:

    def calculate_expiry(
        self,
        purchase_date: str,
        warranty_months: int
    ) -> str:

        purchase = date.fromisoformat(purchase_date)

        expiry = purchase + relativedelta(
            months=warranty_months
        )

        return expiry.isoformat()

    def get_status(
        self,
        purchase_date: str,
        warranty_months: int,
        today: date | None = None
    ) -> dict:

        purchase = date.fromisoformat(purchase_date)

        if today is None:
            today = date.today()

        expiry = purchase + relativedelta(
            months=warranty_months
        )

        # Treat the warranty as active through the expiry date.
        status = "active" if today <= expiry else "expired"

        return {
            "purchase_date": purchase.isoformat(),
            "warranty_months": warranty_months,
            "warranty_expiry": expiry.isoformat(),
            "status": status
        }