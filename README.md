<div align="center">

# ⚡ WarrantyVault

### AI-Powered Receipt Intelligence & Warranty Management

**From an unstructured receipt to a searchable digital asset — automatically.**

<br>

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge)](https://ollama.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-OCR-00A67E?style=for-the-badge)](https://github.com/PaddlePaddle/PaddleOCR)

</div>

---

# The Problem

Receipts are valuable documents, but they were never designed to be
machine-readable databases.

A single purchase receipt can contain:

- Product information
- Seller information
- Invoice / order numbers
- Purchase dates
- Prices
- Warranty information
- Warranty terms
- Supporting documents

But this information usually lives inside **images, PDFs, emails and
scanned documents**.

That creates a surprisingly simple problem:

> **"Is my laptop still under warranty?"**

To answer that manually, a user may need to:

```text
Find the receipt
      ↓
Open the document
      ↓
Identify the product
      ↓
Find the purchase date
      ↓
Find the warranty period
      ↓
Calculate the warranty expiry
      ↓
Determine the current status
