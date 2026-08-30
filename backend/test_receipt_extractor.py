import sys
from pathlib import Path

from backend.app.services.ocr_service import OCRService
from backend.app.services.receipt_extractor import ReceiptExtractor


def main():

    # -------------------------------------------------
    # Require an explicit image path.
    # Example:
    # python -m backend.test_receipt_extractor data/raw/acer.jpg
    # -------------------------------------------------

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python -m backend.test_receipt_extractor "
            "data/raw/acer.jpg"
        )

        print(
            "or:"
        )

        print(
            "python -m backend.test_receipt_extractor "
            "data/raw/samsung.jpg"
        )

        return

    image_path = Path(
        sys.argv[1]
    )

    print(
        f"Testing image: {image_path.resolve()}"
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: "
            f"{image_path.resolve()}"
        )

    ocr_service = OCRService()
    extractor = ReceiptExtractor()

    print(
        "\nRunning OCR..."
    )

    ocr_results = (
        ocr_service.extract_text(
            str(image_path)
        )
    )

    print(
        f"OCR completed: "
        f"{len(ocr_results)} results"
    )

    print(
        "\nRunning receipt extraction..."
    )

    receipt = extractor.extract(
        ocr_results
    )

    print(
        "\n========== STRUCTURED RECEIPT ==========\n"
    )

    for key, value in receipt.items():

        print(
            f"{key}: {value}"
        )

    print(
        "\nTest completed."
    )


if __name__ == "__main__":
    main()