from backend.app.services.ocr_service import OCRService


ocr_service = OCRService()

image_path = "../data/raw/demo.jpg"

results = ocr_service.extract_text(image_path)

print("\n========== OCR RESULT ==========\n")

for item in results:
    print(
        f"{item['confidence']:.3f}  |  {item['text']}"
    )