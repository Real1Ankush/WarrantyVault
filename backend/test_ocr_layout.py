from pathlib import Path

from backend.app.services.ocr_service import OCRService


image_path = Path("data/raw/acer.jpg")

if not image_path.exists():
    raise FileNotFoundError(
        f"Image not found: {image_path.resolve()}"
    )


ocr_service = OCRService()

print("Running OCR...\n")

results = ocr_service.extract_text(
    str(image_path)
)

print("\n========== OCR LAYOUT ==========\n")

for index, item in enumerate(results):

    print(
        f"{index:03d} | "
        f"score={item['confidence']:.3f} | "
        f"box={item['box']} | "
        f"text={item['text']}"
    )