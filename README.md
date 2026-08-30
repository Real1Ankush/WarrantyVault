<div align="center">

# ⚡ WarrantyVault

### AI-powered receipt intelligence & warranty management

**Turn messy receipts into searchable assets, warranty information, and actionable answers.**

<br>

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-OCR-00A67E?style=for-the-badge)](https://github.com/PaddlePaddle/PaddleOCR)

</div>

---

## 🧠 The Problem

Receipts contain valuable information — but they're usually trapped inside
images, PDFs, emails and paper documents.

Finding something as simple as:

> **"Is my laptop still under warranty?"**

can mean manually searching through old files, finding the receipt,
checking the purchase date, finding the warranty terms and calculating
whether the warranty is still valid.

### WarrantyVault turns that entire process into a pipeline.

```text
             📄 RECEIPT
                 │
                 ▼
        ┌─────────────────┐
        │  AI / VISION    │
        │   PROCESSING    │
        └────────┬────────┘
                 │
          extraction fails?
                 │
                 ▼
        ┌─────────────────┐
        │    PaddleOCR    │
        │    FALLBACK     │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ STRUCTURED DATA │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ WARRANTY ENGINE │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  DIGITAL ASSET  │
        │     WALLET      │
        └────────┬────────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
      🔎 SEARCH      🤖 ASSISTANT
