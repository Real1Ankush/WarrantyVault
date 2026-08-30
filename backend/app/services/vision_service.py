import base64
import json
import requests
from datetime import datetime

from backend.app.services.ocr_service import OCRService
from backend.app.services.receipt_extractor import ReceiptExtractor


class VisionExtractionError(Exception):
    """Raised when vision-based receipt extraction fails."""


class VisionService:

    def __init__(self):
        self.ocr_service = OCRService()
        self.receipt_extractor = ReceiptExtractor()

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

    def extract_receipt(self, image_path: str):

        try:
            return self._extract_with_vision(image_path)

        except VisionExtractionError as vision_error:

            print(
                f"Vision extraction failed: {vision_error}"
            )

            print(
                "Falling back to PaddleOCR..."
            )

            try:

                ocr_results = (
                    self.ocr_service.extract_text(
                        image_path
                    )
                )

                if not ocr_results:
                    raise VisionExtractionError(
                        "PaddleOCR returned no text."
                    )

                receipt = (
                    self.receipt_extractor.extract(
                        ocr_results
                    )
                )

                if not receipt:
                    raise VisionExtractionError(
                        "ReceiptExtractor returned no data."
                    )

                return receipt

            except Exception as fallback_error:

                raise VisionExtractionError(
                    "Both vision extraction and "
                    "PaddleOCR fallback failed."
                ) from fallback_error

    def _extract_with_vision(self, image_path: str):

        image_base64 = self._load_image_base64(
            image_path
        )

        prompt = """
Analyze this invoice image and extract the
purchased product and invoice information.

Use the visual layout of the invoice.
Do not rely on assumptions.

IMPORTANT RULES:

1. Do not invent information.

2. seller:
   Return the business/vendor/merchant that sold
   the product.
   Do not return the customer's name.

3. invoice_number:
   Return the value next to Invoice Number,
   Invoice No, Invoice #, or equivalent.

4. order_number:
   Return the value next to Order Number,
   Order No, Order #, or equivalent.

5. order_date:
   Return the date explicitly associated with
   Order Date.

6. invoice_date:
   Return the date explicitly associated with
   Invoice Date.

7. purchase_date:
   Prefer the actual purchase/order date.
   If there is no separate purchase date,
   use order_date.
   If neither exists, use invoice_date.

8. product:
   Return ONLY the actual purchased product
   description.

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

9. product_id:
   Return a product identifier only if it is
   clearly associated with the purchased product.

10. quantity:
    Return the quantity from the product row.

11. total_amount:
    Return the FINAL invoice total.

    Do NOT return:
    - unit price
    - tax amount
    - discount
    - subtotal
    - individual tax value

12. Dates must use YYYY-MM-DD when unambiguous.

13. If something cannot be determined reliably,
    return null.

Return ONLY the JSON object matching the schema.
"""

        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        image_base64
                    ]
                }
            ],
            "stream": False,
            "think": False,
            "format": self.RECEIPT_SCHEMA,
            "options": {
                "temperature": 0
            }
        }

        try:

            response = requests.post(
                self.OLLAMA_URL,
                json=payload,
                timeout=300
            )

        except requests.exceptions.Timeout as error:

            raise VisionExtractionError(
                "Vision model request timed out."
            ) from error

        except requests.exceptions.ConnectionError as error:

            raise VisionExtractionError(
                "Could not connect to Ollama."
            ) from error

        except requests.exceptions.RequestException as error:

            raise VisionExtractionError(
                "Vision model request failed."
            ) from error

        if response.status_code != 200:

            raise VisionExtractionError(
                f"Ollama returned HTTP "
                f"{response.status_code}."
            )

        data = response.json()

        message = data.get(
            "message",
            {}
        )

        raw_response = str(
            message.get(
                "content",
                ""
            )
        ).strip()

        if not raw_response:
            raise VisionExtractionError(
                "Vision model returned an empty response."
            )

        try:

            structured = json.loads(
                raw_response
            )

        except json.JSONDecodeError as error:

            raise VisionExtractionError(
                "Vision model returned invalid JSON."
            ) from error

        self._validate_receipt(structured)

        # Convert model-generated literal "null" strings
        # into actual None values.
        for field in (
            "seller",
            "invoice_number",
            "order_number",
            "order_date",
            "invoice_date",
            "purchase_date",
            "product",
            "product_id",
        ):
            if isinstance(structured[field], str):
                if structured[field].strip().lower() == "null":
                    structured[field] = None

        # Normalize dates after null-string cleanup.
        for field in (
            "order_date",
            "invoice_date",
            "purchase_date",
        ):
            structured[field] = self._normalize_date(
                structured[field]
            )

        # A response containing no meaningful receipt
        # information is not a successful extraction.
        meaningful_fields = (
            "seller",
            "invoice_number",
            "order_number",
            "order_date",
            "invoice_date",
            "purchase_date",
            "product",
            "product_id",
            "quantity",
            "total_amount",
        )

        if not any(
            structured[field] is not None
            for field in meaningful_fields
        ):
            raise VisionExtractionError(
                "Vision model could not identify receipt information."
            )

        return structured

    def _validate_receipt(self, data):

        required_fields = [
            "seller",
            "invoice_number",
            "order_number",
            "order_date",
            "invoice_date",
            "purchase_date",
            "product",
            "product_id",
            "quantity",
            "total_amount",
        ]

        if not isinstance(data, dict):
            raise VisionExtractionError(
                "Vision model response must be a JSON object."
            )

        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing_fields:
            raise VisionExtractionError(
                "Vision model response is missing fields: "
                + ", ".join(missing_fields)
            )

        string_fields = [
            "seller",
            "invoice_number",
            "order_number",
            "order_date",
            "invoice_date",
            "purchase_date",
            "product",
            "product_id",
        ]

        for field in string_fields:

            value = data[field]

            if value is not None and not isinstance(
                value,
                str,
            ):
                raise VisionExtractionError(
                    f"Invalid type for {field}: "
                    f"expected string or null."
                )

        quantity = data["quantity"]

        if quantity is not None and (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
        ):
            raise VisionExtractionError(
                "Invalid type for quantity: "
                "expected integer or null."
            )

        total_amount = data["total_amount"]

        if total_amount is not None and (
            isinstance(total_amount, bool)
            or not isinstance(
                total_amount,
                (int, float),
            )
        ):
            raise VisionExtractionError(
                "Invalid type for total_amount: "
                "expected number or null."
            )

    @staticmethod
    def _normalize_date(value):

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        formats = (
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d-%m-%Y",
        )

        for fmt in formats:

            try:
                parsed = datetime.strptime(
                    value,
                    fmt,
                )

                return parsed.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:
                continue

        if "/" in value:

            parts = value.split("/")

            if len(parts) == 3:

                first, second, year = parts

                if (
                    len(first) == 2
                    and len(second) == 2
                    and len(year) == 4
                ):

                    if int(first) > 12:
                        fmt = "%d/%m/%Y"

                    elif int(second) > 12:
                        fmt = "%m/%d/%Y"

                    else:
                        return None

                    try:
                        parsed = datetime.strptime(
                            value,
                            fmt,
                        )

                        return parsed.strftime(
                            "%Y-%m-%d"
                        )

                    except ValueError:
                        return None

        return None

    @staticmethod
    def _load_image_base64(image_path: str):

        try:
            with open(
                image_path,
                "rb"
            ) as image_file:

                return base64.b64encode(
                    image_file.read()
                ).decode("utf-8")

        except FileNotFoundError as error:

            raise VisionExtractionError(
                f"Invoice image not found: {image_path}"
            ) from error

        except OSError as error:

            raise VisionExtractionError(
                f"Could not read invoice image: {image_path}"
            ) from error
