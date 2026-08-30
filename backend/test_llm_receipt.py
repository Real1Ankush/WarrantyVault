import json
import requests

from backend.app.services.ocr_service import OCRService


IMAGE_PATH = "data/raw/demo.jpg"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


RECEIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "seller": {
            "type": ["string", "null"]
        },
        "invoice_number": {
            "type": ["string", "null"]
        },
        "order_number": {
            "type": ["string", "null"]
        },
        "order_date": {
            "type": ["string", "null"]
        },
        "invoice_date": {
            "type": ["string", "null"]
        },
        "purchase_date": {
            "type": ["string", "null"]
        },
        "product": {
            "type": ["string", "null"]
        },
        "product_id": {
            "type": ["string", "null"]
        },
        "quantity": {
            "type": ["integer", "null"]
        },
        "total_amount": {
            "type": ["number", "null"]
        }
    },
    "required": [
        "seller",
        "invoice_number",
        "order_number",
        "order_date",
        "invoice_date",
        "purchase_date",
        "product",
        "product_id",
        "quantity",
        "total_amount"
    ]
}


def main():

    print("Starting LLM receipt test...")
    print()

    # -----------------------------------------
    # 1. OCR
    # -----------------------------------------

    ocr_service = OCRService()

    print("Running PaddleOCR...")

    ocr_results = ocr_service.extract_text(
        IMAGE_PATH
    )

    print(
        f"OCR items found: {len(ocr_results)}"
    )

    # -----------------------------------------
    # 2. Build compact OCR representation
    # -----------------------------------------

    ocr_lines = []

    for index, item in enumerate(ocr_results):

        text = str(
            item.get("text", "")
        ).strip()

        if not text:
            continue

        ocr_lines.append(
            {
                "index": index,
                "text": text,
                "box": item.get("box"),
                "confidence": item.get(
                    "confidence"
                )
            }
        )

    # -----------------------------------------
    # 3. Prompt
    # -----------------------------------------

    prompt = f"""
Extract structured information from this invoice OCR.

IMPORTANT:
The OCR items are ordered approximately from top to bottom
and contain bounding boxes.

Use the text AND its coordinates to determine the role of
each piece of text.

Do not invent values.

FIELD RULES:

seller:
The business/vendor that sold the product.
Do NOT use the customer's name.

invoice_number:
The value associated with labels such as:
Invoice Number, Invoice No, Invoice #, etc.

order_number:
The value associated with:
Order Number, Order No, Order #, etc.

order_date:
The date associated with Order Date.

invoice_date:
The date associated with Invoice Date.

purchase_date:
Use the actual purchase/order date when available.
If there is no separate purchase date, use order_date.
If neither exists, use invoice_date.

product:
The actual purchased product description.
Do NOT include:
- quantity
- price
- tax
- HSN
- SKU
- ASIN
- product ID
- serial number
- table headers
- footer/signature text

product_id:
Extract a product identifier only if one is clearly associated
with the purchased product.

quantity:
Use the quantity from the product row.
Do not confuse it with prices or other numeric columns.

total_amount:
Use the final invoice total.
Do NOT use:
- unit price
- tax amount
- discount
- subtotal
- individual line-item amount

DATES:
Return dates as YYYY-MM-DD whenever the date is unambiguous.

If a field cannot be determined reliably, return null.

Return ONLY the requested JSON object.

OCR DATA:

{json.dumps(ocr_lines, ensure_ascii=False, indent=2)}

JSON schema:

{json.dumps(RECEIPT_SCHEMA, indent=2)}
"""

    # -----------------------------------------
    # 4. Ollama request
    # -----------------------------------------

    print("Sending OCR data to Qwen3...")
    print()

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "format": RECEIPT_SCHEMA,
        "options": {
            "temperature": 0
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    print(
        f"Ollama HTTP status: {response.status_code}"
    )

    response.raise_for_status()

    data = response.json()

    # -----------------------------------------
    # 5. Debug information
    # -----------------------------------------

    print()
    print("========== OLLAMA STATUS ==========")

    print(
        "done:",
        data.get("done")
    )

    print(
        "done_reason:",
        data.get("done_reason")
    )

    print(
        "eval_count:",
        data.get("eval_count")
    )

    # -----------------------------------------
    # 6. Final model response
    # -----------------------------------------

    raw_response = str(
        data.get("response", "")
    ).strip()

    print()
    print("========== RAW LLM RESPONSE ==========")
    print()

    print(raw_response)

    if not raw_response:

        print()
        print(
            "ERROR: Qwen returned an empty final response."
        )

        print()
        print(
            "Full Ollama response:"
        )

        print(
            json.dumps(
                data,
                indent=2
            )
        )

        return

    # -----------------------------------------
    # 7. Parse JSON
    # -----------------------------------------

    try:

        structured = json.loads(
            raw_response
        )

    except json.JSONDecodeError as error:

        print()
        print(
            "ERROR: Response was not valid JSON."
        )

        print(
            error
        )

        return

    # -----------------------------------------
    # 8. Display result
    # -----------------------------------------

    print()
    print(
        "========== STRUCTURED LLM RECEIPT =========="
    )

    for key in RECEIPT_SCHEMA["properties"]:

        print(
            f"{key}: {structured.get(key)}"
        )

    print()
    print(
        "Test completed."
    )


if __name__ == "__main__":
    main()