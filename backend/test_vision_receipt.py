import base64
import json
import sys
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5vl:3b-q4_K_M"

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


def load_image_base64(path: Path) -> str:
    with path.open("rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


def build_prompt() -> str:
    return """
Analyze this invoice image and extract the purchased product
and invoice information.

Use the visual layout of the invoice.
Do not rely on assumptions.

IMPORTANT RULES:

1. Do not invent information.

2. seller:
   Return the business/vendor/merchant that sold the product.
   Do NOT return the customer's name.

3. invoice_number:
   Return the value next to Invoice Number,
   Invoice No, Invoice #, or equivalent.

4. order_number:
   Return the value next to Order Number,
   Order No, Order #, or equivalent.

5. order_date:
   Return the date explicitly associated with Order Date.

6. invoice_date:
   Return the date explicitly associated with Invoice Date.

7. purchase_date:
   Prefer the actual purchase/order date.
   If there is no separate purchase date,
   use order_date.
   If neither exists, use invoice_date.

8. product:
   Return ONLY the actual purchased product description.

   Do NOT include:
   - price
   - quantity
   - tax
   - HSN
   - SKU
   - ASIN
   - product ID
   - serial number
   - table headers
   - footer text
   - signature text
   - warranty text unless it is part of the actual
     product description

9. product_id:
   Return a product identifier only if it is clearly
   associated with the purchased product.

10. quantity:
    Return the quantity from the product row.
    Do not confuse it with prices, dates, HSN,
    serial numbers, or other numeric values.

11. total_amount:
    Return the FINAL invoice total.

    Do NOT return:
    - unit price
    - tax amount
    - discount
    - subtotal
    - individual line-item amount

12. Dates must use YYYY-MM-DD when unambiguous.

13. If something cannot be determined reliably,
    return null.

14. Never copy a value from an unrelated section of the invoice
    merely because it looks like the requested field.

15. Product information must come from the actual product/item
    section of the invoice.

Return ONLY the JSON object matching the supplied schema.
""".strip()


def main():
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python -m backend.test_vision_receipt data/raw/acer.jpg\n"
            "  python -m backend.test_vision_receipt data/raw/samsung.jpg"
        )
        return 1

    image_path = Path(sys.argv[1])

    if not image_path.is_absolute():
        image_path = Path.cwd() / image_path

    print("========== VISION RECEIPT TEST ==========")
    print()
    print(f"Image: {image_path}")
    print(f"Model: {MODEL}")
    print(f"Ollama: {OLLAMA_URL}")
    print()

    if not image_path.exists():
        print("ERROR: Image file does not exist.")
        print(f"Path: {image_path}")
        return 1

    if not image_path.is_file():
        print("ERROR: Path is not a file.")
        return 1

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    if image_path.suffix.lower() not in allowed_extensions:
        print(
            "ERROR: Unsupported image type."
        )
        print(
            f"Supported types: {', '.join(sorted(allowed_extensions))}"
        )
        return 1

    try:
        image_base64 = load_image_base64(image_path)
    except OSError as error:
        print("ERROR: Could not read image.")
        print(error)
        return 1

    print(
        f"Image loaded: {len(image_base64):,} base64 characters"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": build_prompt(),
                "images": [
                    image_base64
                ]
            }
        ],
        "stream": False,
        "think": False,
        "format": RECEIPT_SCHEMA,
        "options": {
            "temperature": 0
        }
    }

    print()
    print("Sending invoice image to Qwen2.5-VL...")
    print()

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )
    except requests.RequestException as error:
        print("ERROR: Could not connect to Ollama.")
        print(error)
        return 1

    print(
        f"Ollama HTTP status: {response.status_code}"
    )

    if response.status_code != 200:
        print()
        print("ERROR: Ollama returned a non-200 response.")
        print(response.text)
        return 1

    try:
        data = response.json()
    except ValueError:
        print()
        print("ERROR: Ollama returned invalid HTTP JSON.")
        print(response.text)
        return 1

    print()
    print("========== OLLAMA STATUS ==========")
    print()
    print("done:", data.get("done"))
    print("done_reason:", data.get("done_reason"))
    print("eval_count:", data.get("eval_count"))

    message = data.get("message")

    if not isinstance(message, dict):
        print()
        print("ERROR: Ollama response did not contain a valid message.")
        print(json.dumps(data, indent=2))
        return 1

    raw_response = str(
        message.get("content", "")
    ).strip()

    print()
    print("========== RAW VISION RESPONSE ==========")
    print()
    print(raw_response)

    if not raw_response:
        print()
        print("ERROR: Vision model returned an empty response.")
        print()
        print("Full Ollama response:")
        print(json.dumps(data, indent=2))
        return 1

    try:
        structured = json.loads(raw_response)
    except json.JSONDecodeError as error:
        print()
        print("ERROR: Vision model returned invalid JSON.")
        print(error)
        return 1

    if not isinstance(structured, dict):
        print()
        print("ERROR: Vision response is not a JSON object.")
        return 1

    print()
    print("========== STRUCTURED VISION RECEIPT ==========")
    print()

    for key in RECEIPT_SCHEMA["properties"]:
        print(
            f"{key}: {structured.get(key)}"
        )

    print()
    print("Test completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())