import re
from datetime import datetime


class ReceiptExtractor:

    # Generic structural labels.
    PRODUCT_HEADER_TERMS = {
        "product",
        "product name",
        "description",
        "item",
        "item name",
        "particulars",
        "particular",
        "details",
    }

    QUANTITY_HEADER_TERMS = {
        "qty",
        "quantity",
    }

    SUMMARY_TERMS = {
        "total",
        "total:",
        "net total",
        "grand total",
        "amount payable",
        "shipping charges",
        "amount in words",
        "authorized signature",
        "authorized signatory",
    }

    SELLER_LABELS = {
        "sold by",
        "seller",
        "vendor",
        "supplier",
        "merchant",
    }

    def extract(self, ocr_results):

        items = []

        for raw in ocr_results:

            text = str(
                raw.get("text", "")
            ).strip()

            if not text:
                continue

            items.append(
                {
                    "text": text,
                    "confidence": self.to_float(
                        raw.get("confidence")
                    ),
                    "box": self.normalize_box(
                        raw.get("box")
                    ),
                }
            )

        lines = [
            item["text"]
            for item in items
        ]

        full_text = "\n".join(lines)

        order_date = self.extract_order_date(
            full_text
        )

        invoice_date = self.extract_invoice_date(
            full_text
        )

        # Explicit rule:
        # order date is preferred for warranty calculations.
        purchase_date = (
            order_date
            or invoice_date
        )

        table = self.detect_item_table(
            items
        )

        product = None
        product_confidence = 0.0

        if table is not None:

            (
                product,
                product_confidence,
            ) = self.extract_product_from_table(
                table
            )

        # Important:
        # Do NOT fall back to arbitrary page text.
        #
        # A wrong product is worse than no product.
        if product is None:

            product_confidence = 0.0

        product_id = self.extract_product_id(
            items
        )

        quantity = self.extract_quantity(
            table
        )

        total_amount = self.extract_total(
            items
        )

        return {
            "seller": self.extract_seller(
                items
            ),

            "invoice_number":
                self.extract_invoice_number(
                    full_text
                ),

            "order_number":
                self.extract_order_number(
                    full_text
                ),

            "order_date": order_date,

            "invoice_date": invoice_date,

            "purchase_date": purchase_date,

            "product": product,

            "product_id": product_id,

            "quantity": quantity,

            "total_amount": total_amount,

            "product_confidence": round(
                product_confidence,
                3,
            ),

            "needs_review": (
                product is None
                or product_confidence < 0.60
            ),
        }

    # =====================================================
    # SELLER
    # =====================================================

    def extract_seller(self, items):

        for label_item in items:

            label = self.normalize_label(
                label_item["text"]
            )

            if label not in self.SELLER_LABELS:
                continue

            label_box = label_item["box"]

            if label_box is None:
                continue

            candidates = []

            for candidate in items:

                box = candidate["box"]

                if box is None:
                    continue

                text = candidate["text"].strip()

                if not text:
                    continue

                # Value must be below label.
                if box[1] < label_box[3]:
                    continue

                vertical_gap = (
                    box[1] - label_box[3]
                )

                # Seller value is normally very close.
                if vertical_gap > 30:
                    continue

                # Horizontal relationship:
                # either boxes overlap or their edges are
                # reasonably close.
                horizontal_overlap = (
                    min(
                        box[2],
                        label_box[2],
                    )
                    -
                    max(
                        box[0],
                        label_box[0],
                    )
                )

                horizontal_distance = min(
                    abs(
                        box[0]
                        - label_box[2]
                    ),
                    abs(
                        box[2]
                        - label_box[0]
                    ),
                )

                related = (
                    horizontal_overlap > 0
                    or horizontal_distance <= 70
                )

                if not related:
                    continue

                if self.looks_like_address(
                    text
                ):
                    continue

                if self.looks_like_field_label(
                    text
                ):
                    continue

                candidates.append(
                    (
                        vertical_gap,
                        horizontal_distance,
                        candidate,
                    )
                )

            if candidates:

                candidates.sort(
                    key=lambda x: (
                        x[0],
                        x[1],
                    )
                )

                return candidates[0][2][
                    "text"
                ]

        return None

    # =====================================================
    # INVOICE NUMBER
    # =====================================================

    def extract_invoice_number(
        self,
        text,
    ):

        patterns = [
            r"Invoice\s+Number\s*:\s*"
            r"([A-Za-z0-9\-_/#]+)",

            r"Invoice\s+No\.?\s*:\s*"
            r"([A-Za-z0-9\-_/#]+)",

            r"Invoice\s*#\s*:\s*"
            r"([A-Za-z0-9\-_/#]+)",
        ]

        return self.first_match(
            text,
            patterns,
        )

    # =====================================================
    # ORDER NUMBER
    # =====================================================

    def extract_order_number(
        self,
        text,
    ):

        patterns = [
            r"Order\s+Number\s*:\s*"
            r"([A-Za-z0-9\-_/#]+)",

            r"Order\s+No\.?\s*:\s*"
            r"([A-Za-z0-9\-_/#]+)",

            r"Order\s*#\s*:\s*"
            r"([A-Za-z0-9\-_/#]+)",
        ]

        return self.first_match(
            text,
            patterns,
        )

    # =====================================================
    # DATES
    # =====================================================

    def extract_order_date(
        self,
        text,
    ):

        return self.extract_labeled_date(
            text,
            "Order Date",
        )

    def extract_invoice_date(
        self,
        text,
    ):

        return self.extract_labeled_date(
            text,
            "Invoice Date",
        )

    def extract_labeled_date(
        self,
        text,
        label,
    ):

        escaped = re.escape(label)

        patterns = [
            rf"{escaped}\s*:\s*"
            r"(\d{2}\.\d{2}\.\d{4})",

            rf"{escaped}\s*:\s*"
            r"(\d{2}/\d{2}/\d{4})",

            rf"{escaped}\s*:\s*"
            r"(\d{2}-\d{2}-\d{4})",
        ]

        value = self.first_match(
            text,
            patterns,
        )

        if value is None:
            return None

        for fmt in (
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ):

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

        return None

    # =====================================================
    # TABLE DETECTION
    # =====================================================

    def detect_item_table(
        self,
        items,
    ):

        rows = self.group_rows(
            items
        )

        candidates = []

        for row_index, row in enumerate(
            rows
        ):

            product_headers = []
            quantity_headers = []
            other_headers = []

            for item in row:

                label = self.normalize_label(
                    item["text"]
                )

                if self.is_product_header(
                    label
                ):

                    product_headers.append(
                        item
                    )

                elif self.is_quantity_header(
                    label
                ):

                    quantity_headers.append(
                        item
                    )

                elif self.is_other_table_header(
                    label
                ):

                    other_headers.append(
                        item
                    )

            if not product_headers:
                continue

            # We need evidence that this is really a
            # table, not an ordinary sentence.
            header_count = (
                len(product_headers)
                + len(quantity_headers)
                + len(other_headers)
            )

            if header_count < 2:
                continue

            score = (
                len(product_headers) * 4
                + len(quantity_headers) * 2
                + len(other_headers)
            )

            candidates.append(
                {
                    "header_index": row_index,
                    "row": row,
                    "rows_after": rows[
                        row_index + 1:
                    ],
                    "product_header": (
                        product_headers[0]
                    ),
                    "quantity_header": (
                        quantity_headers[0]
                        if quantity_headers
                        else None
                    ),
                    "score": score,
                }
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda candidate:
            candidate["score"],
            reverse=True,
        )

        return candidates[0]

    # =====================================================
    # ROW GROUPING
    # =====================================================

    def group_rows(
        self,
        items,
        tolerance=10,
    ):

        usable = [
            item
            for item in items
            if item["box"] is not None
        ]

        usable.sort(
            key=lambda item: (
                self.center_y(
                    item["box"]
                ),
                self.box_left(
                    item["box"]
                ),
            )
        )

        rows = []

        for item in usable:

            cy = self.center_y(
                item["box"]
            )

            placed = False

            for row in rows:

                avg_y = sum(
                    self.center_y(
                        member["box"]
                    )
                    for member in row
                ) / len(row)

                if abs(
                    cy - avg_y
                ) <= tolerance:

                    row.append(item)
                    placed = True
                    break

            if not placed:

                rows.append(
                    [item]
                )

        for row in rows:

            row.sort(
                key=lambda item:
                self.box_left(
                    item["box"]
                )
            )

        return rows

    # =====================================================
    # HEADER CLASSIFICATION
    # =====================================================

    def is_product_header(
        self,
        text,
    ):

        text = self.normalize_label(text)

        # These are product-column concepts, but not valid
        # product values themselves.
        if text in {
            "product",
            "product name",
            "description",
            "item",
            "item name",
            "particulars",
            "particular",
        }:
            return True

        # "details" alone is too ambiguous to define a
        # product column.
        if text == "details":
            return True

        return (
            "product " in text
            or text.startswith("product ")
            or "description" in text
            or "particular" in text
        )

    def is_invalid_product_candidate(self, text):

        normalized = self.normalize_label(text)

        invalid = {
            "price",
            "unit price",
            "amount",
            "total",
            "total amount",
            "discount",
            "qty",
            "quantity",
            "net",
            "net amount",
            "tax",
            "tax rate",
            "tax type",
            "tax amount",
            "hsn",
            "value",
            "cgst",
            "sgst",
            "igst",
            "description",
            "product",
            "product name",
            "item",
            "item name",
            "particulars",
            "particular",
            "details",
        }

        return normalized in invalid

    def is_quantity_header(
        self,
        text,
    ):

        return (
            text == "qty"
            or text == "quantity"
            or "qty" in text
        )

    def is_other_table_header(
        self,
        text,
    ):

        structural_terms = (
            "hsn",
            "unit price",
            "price",
            "discount",
            "tax",
            "total",
            "amount",
            "net",
            "value",
            "cgst",
            "sgst",
            "igst",
            "serial",
            "s.no",
            "no",
        )

        return any(
            term in text
            for term in structural_terms
        )

    # =====================================================
    # PRODUCT EXTRACTION
    # =====================================================

    def extract_product_from_table(
        self,
        table,
    ):

        header_box = table[
            "product_header"
        ]["box"]

        if header_box is None:
            return None, 0.0

        product_left = header_box[0]

        # Find the nearest structural header to the
        # right of the product header.
        right_edge = self.find_product_right_edge(
            table["row"],
            product_left,
        )

        if right_edge is None:
            return None, 0.0

        rows = table[
            "rows_after"
        ]

        first_item_index = None
        first_parts = []

        # -------------------------------------------------
        # Find first actual item row
        # -------------------------------------------------

        for index, row in enumerate(
            rows
        ):

            if self.is_summary_row(
                row
            ):
                break

            parts = []

            for item in row:

                box = item["box"]

                if box is None:
                    continue

                center_x = self.center_x(
                    box
                )

                if not (
                    product_left
                    <= center_x
                    < right_edge
                ):
                    continue

                text = item["text"].strip()

                if not text:
                    continue

                if self.is_standalone_product_id(
                    text
                ):
                    break

                if self.is_summary_text(
                    text
                ):
                    break

                if self.is_serial_number(
                    text
                ):
                    continue

                if self.looks_numeric(
                    text
                ):
                    continue

                if self.is_invalid_product_candidate(
                    text
                ):
                    continue

                parts.append(text)

            if parts:

                first_item_index = index
                first_parts = parts
                break

        if first_item_index is None:
            return None, 0.0

        product_parts = list(
            first_parts
        )

        previous_y = self.center_y(
            rows[first_item_index][0][
                "box"
            ]
        )

        # -------------------------------------------------
        # Collect wrapped product lines.
        # -------------------------------------------------

        for row in rows[
            first_item_index + 1:
        ]:

            if self.is_summary_row(
                row
            ):
                break

            current_y = self.center_y(
                row[0]["box"]
            )

            vertical_gap = (
                current_y
                - previous_y
            )

            # Wrapped OCR lines are very close.
            if vertical_gap > 20:
                break

            row_parts = []

            for item in row:

                box = item["box"]

                if box is None:
                    continue

                center_x = self.center_x(
                    box
                )

                if not (
                    product_left
                    <= center_x
                    < right_edge
                ):
                    continue

                text = item["text"].strip()

                if not text:
                    continue

                if self.is_standalone_product_id(
                    text
                ):
                    break

                if self.is_summary_text(
                    text
                ):
                    break

                if self.is_serial_number(
                    text
                ):
                    continue

                if self.looks_numeric(
                    text
                ):
                    continue

                if self.is_invalid_product_candidate(
                    text
                ):
                    continue

                row_parts.append(
                    text
                )

            if not row_parts:
                break

            product_parts.extend(
                row_parts
            )

            previous_y = current_y

        product = self.clean_product(
            " ".join(product_parts)
        )

        if not product:
            return None, 0.0

        confidence = 0.80

        if len(product_parts) > 1:
            confidence += 0.08

        if len(product) >= 20:
            confidence += 0.05

        if self.looks_like_business_name(
            product
        ):
            confidence -= 0.30

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        return product, confidence

    # =====================================================
    # PRODUCT COLUMN RIGHT EDGE
    # =====================================================

    def find_product_right_edge(
        self,
        header_row,
        product_left,
    ):

        right_headers = []

        for item in header_row:

            box = item["box"]

            if box is None:
                continue

            if box[0] <= product_left:
                continue

            label = self.normalize_label(
                item["text"]
            )

            if self.is_product_header(
                label
            ):
                continue

            if (
                self.is_quantity_header(
                    label
                )
                or self.is_other_table_header(
                    label
                )
            ):

                right_headers.append(
                    box[0]
                )

        if right_headers:
            return min(
                right_headers
            )

        return None

    # =====================================================
    # PRODUCT ID
    # =====================================================

    def extract_product_id(
        self,
        items,
    ):

        for item in items:

            text = item["text"].strip()
            compact = re.sub(
                r"\s+",
                "",
                text.upper(),
            )

            # Amazon ASIN.
            match = re.fullmatch(
                r"(B0[A-Z0-9]{8})"
                r"(?:\(B0[A-Z0-9]{8}\))?\s*",
                compact,
            )

            if match:
                return match.group(1)

            # Repeated identifier.
            repeated = re.fullmatch(
                r"([A-Z0-9][A-Z0-9\-_/.]{5,})"
                r"\(\1\)",
                compact,
            )

            if repeated:
                return repeated.group(1)

        # Explicit product-id labels remain a fallback.
        labels = (
            "product id",
            "product code",
            "sku",
            "model no",
            "model number",
        )

        for index, item in enumerate(
            items
        ):

            label = self.normalize_label(
                item["text"]
            )

            if not any(
                key in label
                for key in labels
            ):
                continue

            for candidate in items[
                index + 1:
                index + 5
            ]:

                value = candidate[
                    "text"
                ].strip()

                if self.is_identifier(
                    value
                ):
                    return value

        return None

    # =====================================================
    # QUANTITY
    # =====================================================

    def extract_quantity(
        self,
        table,
    ):

        if table is None:
            return None

        quantity_header = table[
            "quantity_header"
        ]

        if quantity_header is None:
            return None

        header_box = quantity_header[
            "box"
        ]

        if header_box is None:
            return None

        header_x = self.center_x(
            header_box
        )

        rows = table[
            "rows_after"
        ]

        for row in rows:

            if self.is_summary_row(
                row
            ):
                break

            for item in row:

                box = item["box"]

                if box is None:
                    continue

                center_x = self.center_x(
                    box
                )

                if abs(
                    center_x - header_x
                ) > 30:
                    continue

                value = self.extract_plain_integer(
                    item["text"]
                )

                if value is not None:
                    return value

        return None

    # =====================================================
    # TOTAL
    # =====================================================

    def extract_total(
        self,
        items,
    ):

        summary_candidates = []

        for item in items:

            text = item["text"].strip()

            lower = text.lower()

            if (
                "net total" in lower
                or "grand total" in lower
                or lower == "total:"
                or lower.startswith("total:")
                or "amount payable"
                in lower
            ):

                if item["box"] is not None:

                    summary_candidates.append(
                        item
                    )

        summary_candidates.sort(
            key=lambda item:
            self.center_y(
                item["box"]
            )
        )

        for summary in reversed(
            summary_candidates
        ):

            summary_box = summary[
                "box"
            ]

            summary_y = self.center_y(
                summary_box
            )

            candidates = []

            for item in items:

                box = item["box"]

                if box is None:
                    continue

                item_y = self.center_y(
                    box
                )

                if abs(
                    item_y - summary_y
                ) > 35:
                    continue

                amounts = self.extract_amounts(
                    item["text"]
                )

                if not amounts:
                    continue

                # When one OCR box contains multiple amounts,
                # use its final/rightmost total.
                final_amount = amounts[-1]

                candidates.append(
                    (
                        abs(item_y - summary_y),
                        box[2],
                        final_amount,
                    )
                )

            if candidates:

                candidates.sort(
                    key=lambda x: (
                        x[0],
                        -x[1],
                    )
                )

                return candidates[0][2]

        # Fallback: use the lowest/rightmost monetary
        # value on the document.
        monetary = []

        for item in items:

            box = item["box"]

            if box is None:
                continue

            amounts = self.extract_amounts(
                item["text"]
            )

            for amount in amounts:

                monetary.append(
                    (
                        self.center_y(
                            box
                        ),
                        box[2],
                        amount,
                    )
                )

        if monetary:

            monetary.sort(
                key=lambda x: (
                    x[0],
                    x[1],
                )
            )

            return monetary[-1][2]

        return None

    # =====================================================
    # TABLE/STOP HELPERS
    # =====================================================

    def is_summary_row(
        self,
        row,
    ):

        for item in row:

            if self.is_summary_text(
                item["text"]
            ):
                return True

        return False

    def is_summary_text(
        self,
        text,
    ):

        normalized = self.normalize_label(
            text
        )

        if normalized in self.SUMMARY_TERMS:
            return True

        return (
            normalized.startswith(
                "hsn:"
            )
            or normalized.startswith(
                "shipping charges"
            )
            or normalized.startswith(
                "net total"
            )
            or normalized.startswith(
                "grand total"
            )
            or normalized.startswith(
                "authorized signature"
            )
            or normalized.startswith(
                "authorized signatory"
            )
        )

    # =====================================================
    # PRODUCT ID
    # =====================================================

    def is_standalone_product_id(
        self,
        text,
    ):

        normalized = text.strip().upper()

        # Remove whitespace around parentheses.
        compact = re.sub(
            r"\s+",
            "",
            normalized,
        )

        # ASIN / Amazon-style IDs.
        if re.fullmatch(
            r"B0[A-Z0-9]{8}"
            r"(?:\(B0[A-Z0-9]{8}\))?",
            compact,
        ):
            return True

        # Generic repeated-ID pattern, such as
        # ABC123(ABC123).
        repeated = re.fullmatch(
            r"([A-Z0-9][A-Z0-9\-_/.]{5,})"
            r"\(\1\)",
            compact,
        )

        if repeated:
            return True

        return False

    # =====================================================
    # MISC HELPERS
    # =====================================================

    def looks_numeric(
        self,
        text,
    ):

        value = (
            text
            .strip()
        )

        if re.search(
            r"(?:₹|Rs\.?|R)\s*"
            r"\d",
            value,
            re.IGNORECASE,
        ):
            return True

        if re.fullmatch(
            r"[-+]?"
            r"\d+(?:[.,]\d+)*",
            value,
        ):
            return True

        return False

    def extract_plain_integer(
        self,
        text,
    ):

        value = text.strip()

        if not re.fullmatch(
            r"\d+",
            value,
        ):
            return None

        try:
            return int(value)
        except ValueError:
            return None

    def is_serial_number(
        self,
        text,
    ):

        return bool(
            re.fullmatch(
                r"\d{1,3}",
                text.strip(),
            )
        )

    def is_identifier(
        self,
        text,
    ):

        if len(text) < 4:
            return False

        if len(text) > 40:
            return False

        if text.isdigit():
            return False

        return bool(
            re.fullmatch(
                r"[A-Za-z0-9]"
                r"[A-Za-z0-9\-_/.]+",
                text,
            )
        )

    def looks_like_business_name(
        self,
        text,
    ):

        upper = text.upper()

        patterns = (
            "PRIVATE LTD",
            "PVT LTD",
            "MOBILE WORLD",
            "RETAIL",
            "TRADERS",
            "ENTERPRISES",
            "CORPORATION",
            "CORP",
        )

        return any(
            p in upper
            for p in patterns
        )

    def looks_like_address(
        self,
        text,
    ):

        lower = text.lower()

        patterns = (
            "address",
            "road",
            "street",
            "sector",
            "colony",
            "nagar",
            "india",
            "west bengal",
            "madhya pradesh",
            "karnataka",
            "delhi",
        )

        return any(
            p in lower
            for p in patterns
        )

    def looks_like_field_label(
        self,
        text,
    ):

        normalized = self.normalize_label(
            text
        )

        return (
            normalized in {
                "billing address",
                "shipping address",
                "invoice details",
                "invoice number",
                "invoice no",
                "order number",
                "order no",
                "payment",
                "method",
                "channel",
            }
            or normalized.endswith(":")
        )

    def extract_amounts(
        self,
        text,
    ):

        matches = re.findall(
            r"(?:₹|Rs\.?|R)?\s*"
            r"(\d+(?:,\d{3})*"
            r"\.\d{2})",
            text,
            re.IGNORECASE,
        )

        values = []

        for value in matches:

            try:
                values.append(
                    float(
                        value.replace(
                            ",",
                            "",
                        )
                    )
                )
            except ValueError:
                pass

        return values

    def first_match(
        self,
        text,
        patterns,
    ):

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return (
                    match.group(1)
                    .strip()
                )

        return None

    def normalize_label(
        self,
        text,
    ):

        value = text.lower().strip()

        value = re.sub(
            r"[\s:]+$",
            "",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value

    def clean_product(
        self,
        text,
    ):

        value = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        return value or None

    # =====================================================
    # BOX HELPERS
    # =====================================================

    def normalize_box(
        self,
        box,
    ):

        if box is None:
            return None

        if (
            isinstance(
                box,
                (list, tuple),
            )
            and len(box) == 4
        ):

            try:

                return [
                    float(box[0]),
                    float(box[1]),
                    float(box[2]),
                    float(box[3]),
                ]

            except (
                TypeError,
                ValueError,
            ):
                return None

        if (
            isinstance(
                box,
                (list, tuple),
            )
            and len(box) >= 4
        ):

            try:

                xs = [
                    float(point[0])
                    for point in box
                ]

                ys = [
                    float(point[1])
                    for point in box
                ]

                return [
                    min(xs),
                    min(ys),
                    max(xs),
                    max(ys),
                ]

            except (
                TypeError,
                ValueError,
                IndexError,
            ):
                return None

        return None

    def center_x(
        self,
        box,
    ):

        return (
            box[0] + box[2]
        ) / 2

    def center_y(
        self,
        box,
    ):

        return (
            box[1] + box[3]
        ) / 2

    def box_left(
        self,
        box,
    ):

        return box[0]

    def to_float(
        self,
        value,
    ):

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0
