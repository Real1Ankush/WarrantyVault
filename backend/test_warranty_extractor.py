from backend.app.services.ocr_service import OCRService
from backend.app.services.warranty_extractor import WarrantyExtractor
from pathlib import Path


ocr_service = OCRService()
extractor = WarrantyExtractor()

image_path = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "warranty.png"
)

print("\nRunning OCR...\n")

ocr_results = ocr_service.extract_text(image_path)

print("OCR completed.")
print(f"OCR results: {len(ocr_results)}")

print("\nRunning warranty extraction...\n")

warranty = extractor.extract(ocr_results)

print("========== WARRANTY EXTRACTION ==========\n")

for key, value in warranty.items():
    print(f"{key}: {value}")
