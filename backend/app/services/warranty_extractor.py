import re


class WarrantyExtractor:

    def extract(self, ocr_results):

        text_lines = [
            item["text"].strip()
            for item in ocr_results
        ]

        full_text = " ".join(text_lines)

        warranty_months = self.extract_months(full_text)

        return {
            "warranty_months": warranty_months
        }

    def extract_months(self, text):

        # Examples:
        # 12 MONTHS
        # 12 months warranty
        # Warranty: 12 months
        # 1 year warranty

        month_pattern = r"\b(\d+)\s*months?\b"

        match = re.search(
            month_pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

        # Convert years to months.
        year_pattern = r"\b(\d+)\s*years?\b"

        match = re.search(
            year_pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1)) * 12

        return None
    