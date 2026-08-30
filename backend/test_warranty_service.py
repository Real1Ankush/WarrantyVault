from datetime import date

from backend.app.services.warranty_service import WarrantyService


service = WarrantyService()


result = service.get_status(
    purchase_date="2025-08-12",
    warranty_months=12,
    today=date(2026, 8, 10)
)


print("\n========== WARRANTY RESULT ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")