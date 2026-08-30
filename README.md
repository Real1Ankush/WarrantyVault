# WarrantyVault

### An AI-powered digital receipt & warranty wallet

> **Upload a receipt. Extract the purchase. Track the warranty. Ask the assistant.**

WarrantyVault turns unstructured purchase documents into structured, searchable
digital assets.

Instead of searching through old emails, PDFs and images to answer:

> *"Is my laptop still under warranty?"*

WarrantyVault processes the purchase document, extracts the important details,
stores them as an asset, calculates warranty information and lets you interact
with your purchases through a natural-language assistant.

---

## The Idea

Receipts are designed for humans to read once — not for software to understand.

A single receipt may contain:

- Product information
- Seller information
- Invoice number
- Order number
- Purchase date
- Invoice date
- Total amount
- Warranty information

WarrantyVault converts this:

```text
┌─────────────────────────┐
│       RAW RECEIPT       │
│                         │
│  Product: Acer Nitro 5  │
│  Seller: Appario        │
│  Amount: ₹46,989        │
│  Invoice: SCCC-699517   │
│  Date: 29/12/2019       │
└────────────┬────────────┘
             │
             ▼
       AI DOCUMENT
        PROCESSING
             │
             ▼
┌─────────────────────────┐
│    STRUCTURED ASSET     │
│                         │
│ Product                 │
│ Seller                  │
│ Invoice                 │
│ Purchase Date           │
│ Amount                  │
│ Warranty                │
│ Documents               │
└─────────────────────────┘
