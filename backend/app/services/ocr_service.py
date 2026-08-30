import os

# Disable problematic oneDNN/PIR path on our current Windows CPU setup.
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR


class OCRService:

    def __init__(self):
        self.ocr = None

    def _get_engine(self):
        if self.ocr is None:
            self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
            )

        return self.ocr

    def extract_text(self, image_path: str):

        results = self._get_engine().predict(str(image_path))

        extracted_data = []

        for result in results:

            # PaddleOCR 3.x result object
            result_data = result.json

            # Some versions expose json as a method.
            if callable(result_data):
                result_data = result_data()

            res = result_data["res"]

            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])

            # Depending on PaddleOCR version, boxes may be
            # lists or NumPy arrays.
            boxes = res.get("rec_boxes")

            if boxes is None:
                boxes = res.get("rec_polys")

            for index, text in enumerate(texts):

                score = (
                    float(scores[index])
                    if index < len(scores)
                    else None
                )

                box = (
                    boxes[index]
                    if index < len(boxes)
                    else None
                )

                # Convert NumPy arrays if necessary.
                # Leave Python lists unchanged.
                if box is not None:
                    try:
                        box = box.tolist()
                    except AttributeError:
                        pass

                extracted_data.append(
                    {
                        "text": str(text),
                        "confidence": score,
                        "box": box,
                    }
                )

        return extracted_data
