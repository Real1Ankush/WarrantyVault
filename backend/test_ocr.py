import os

# Disable the problematic oneDNN/PIR path.
# These must be set before importing PaddleOCR.
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_use_mkldnn"] = "0"

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False,
)

image_path = "data/raw/demo.jpg"

results = ocr.predict(image_path)

for result in results:
    result.print()  