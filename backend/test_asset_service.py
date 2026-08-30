from datetime import date
from pathlib import Path

from backend.app.services.ocr_service import OCRService
from backend.app.services.receipt_extractor import ReceiptExtractor
from backend.app.services.warranty_extractor import WarrantyExtractor
from backend.app.services.asset_service import AssetService


ocr_service = OCRService()

receipt_extractor = ReceiptExtractor()
warranty_extractor = WarrantyExtractor()
asset_service = AssetService()


# ---------- RECEIPT ----------
data_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
receipt_image = data_dir / "demo1.jpg"

print("\nProcessing receipt...")

receipt_ocr = ocr_service.extract_text(receipt_image)
receipt = receipt_extractor.extract(receipt_ocr)


# ---------- WARRANTY ----------
warranty_image = data_dir / "warranty.png"

print("Processing warranty document...")

warranty_ocr = ocr_service.extract_text(warranty_image)
warranty = warranty_extractor.extract(warranty_ocr)


# ---------- COMBINE ----------
asset = asset_service.build_asset_record(
    receipt=receipt,
    warranty=warranty,
    today=date(2026, 8, 15)
)


print("\n========== DIGITAL ASSET ==========\n")

for key, value in asset.items():
    print(f"{key}: {value}")
