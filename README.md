<div align="center">

# ⚡ WarrantyVault

### AI-Powered Receipt Intelligence & Warranty Management

**Turn messy receipts into searchable digital assets — automatically.**

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PaddleOCR-OCR-00A67E?style=for-the-badge" />
</p>

<p>
  <strong>Upload a receipt → Understand it → Build an asset → Track warranty → Ask questions</strong>
</p>

</div>

---

# The Problem

You bought a laptop eight months ago.

Today, something goes wrong.

You know you bought it recently.

But now comes the frustrating part:

- Where is the receipt?
- What was the invoice number?
- What was the actual purchase date?
- Who was the seller?
- How much did you pay?
- When does the warranty expire?
- Is the product still covered?

The information already exists.

It is just trapped inside **images, PDFs, invoices and unstructured documents**.

A receipt is designed for a human to read once.

It isn't designed to become a database record, a searchable object, or something an AI assistant can reason over.

### WarrantyVault solves that gap.

Instead of treating a receipt as a file, WarrantyVault turns it into a **structured digital asset**.

---

# From Receipt → Intelligence

```text
                         ┌──────────────────────┐
                         │     RECEIPT IMAGE    │
                         │       / DOCUMENT     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   VISION PROCESSING  │
                         └──────────┬───────────┘
                                    │
                           extraction successful?
                              ┌─────┴─────┐
                              │           │
                             YES          NO
                              │           │
                              │           ▼
                              │    ┌───────────────┐
                              │    │   PaddleOCR   │
                              │    │    FALLBACK   │
                              │    └───────┬───────┘
                              │            │
                              └─────┬──────┘
                                    ▼
                         ┌──────────────────────┐
                         │ RECEIPT EXTRACTION   │
                         │                      │
                         │ Product              │
                         │ Product ID           │
                         │ Seller               │
                         │ Invoice / Order      │
                         │ Dates                │
                         │ Amount               │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ WARRANTY EXTRACTION  │
                         │                      │
                         │ Duration             │
                         │ Source               │
                         │ Expiry               │
                         │ Status               │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     DIGITAL ASSET    │
                         │                      │
                         │ Structured + Stored  │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
             ┌────────────────┐            ┌────────────────┐
             │    SEMANTIC    │            │      AI        │
             │     SEARCH     │            │   ASSISTANT    │
             └────────────────┘            └───────┬────────┘
                                                   │
                                                   ▼
                                      "Is my laptop still
                                       under warranty?"
```

---

# The Idea

WarrantyVault has one simple principle:

> **Don't store receipts. Understand them.**

A receipt goes through multiple layers of processing.

```text
RAW DOCUMENT
     │
     ▼
VISUAL UNDERSTANDING
     │
     ▼
OCR / TEXT RECOVERY
     │
     ▼
STRUCTURED EXTRACTION
     │
     ▼
WARRANTY LOGIC
     │
     ▼
PERSISTENT DIGITAL ASSET
     │
     ├──────────────► SEARCH
     │
     └──────────────► AI ASSISTANT
```

This turns a static purchase document into something the application can actually work with.

---

# Why This Is More Than OCR

A basic OCR application does this:

```text
Receipt
   ↓
Text
```

WarrantyVault goes further:

```text
Receipt
   ↓
Text + Visual Information
   ↓
Structured Purchase Data
   ↓
Asset
   ↓
Warranty Intelligence
   ↓
Semantic Retrieval
   ↓
AI Assistant
```

The goal isn't simply to **read** the receipt.

The goal is to convert unstructured information into a representation that the rest of the system can **store, search, reason about and use**.

---

# The AI Layer

## Local LLM with Ollama

WarrantyVault uses **Ollama** as the local LLM runtime for AI-powered processing.

The architecture is intentionally designed so that the AI layer works as part of the application pipeline rather than being an isolated chatbot.

```text
                    ┌─────────────────┐
                    │     Receipt     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Vision / OCR    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Extracted Data  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Ollama      │
                    │    Local LLM    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Structured      │
                    │ Information     │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
             Asset Layer          Assistant Layer
```

### Why local inference?

Using Ollama gives the project a local LLM execution layer rather than making the entire system dependent on a remote model API.

That makes the architecture particularly interesting from an engineering perspective:

- document processing
- AI extraction
- local inference
- business logic
- persistence
- retrieval
- natural-language interaction

all operate as parts of one system.

---

# OCR With a Fallback Strategy

Real-world receipts are messy.

They can contain:

- unusual layouts
- small text
- distorted images
- inconsistent formatting
- tables
- logos
- multiple dates
- partially readable fields

Because of that, WarrantyVault does not treat a single extraction mechanism as the only path.

### Primary path

```text
Receipt
   ↓
Vision Processing
   ↓
Structured Extraction
```

### Fallback path

```text
Receipt
   ↓
Vision Processing
   ↓
Extraction Failure
   ↓
PaddleOCR
   ↓
Text Recovery
   ↓
Structured Extraction
```

This is an important design decision:

> **When one perception path fails, the application should have another way to recover useful information.**

---

# What Becomes a Digital Asset?

WarrantyVault represents a purchase as a structured asset rather than just keeping the original document.

A typical asset can contain:

| Field | Purpose |
|---|---|
| Product | Purchased product |
| Product ID | Product identifier when available |
| Seller | Seller / merchant |
| Invoice Number | Invoice reference |
| Order Number | Order reference |
| Order Date | Original order date |
| Invoice Date | Original invoice date |
| Purchase Date | Date selected for warranty calculations |
| Total Amount | Purchase amount |
| Warranty Months | Warranty duration |
| Warranty Source | Where warranty information came from |
| Warranty Expiry | Calculated expiry date |
| Warranty Status | Current warranty state |

This separation between the **original document** and the **structured asset** allows the application to preserve the source while creating useful machine-readable information around it.

---

# Document + Asset Architecture

WarrantyVault separates the uploaded document from the business object created from it.

```text
┌─────────────────────────┐
│        Document         │
│                         │
│ original_filename       │
│ file_path               │
│ mime_type               │
│ uploaded_at             │
└────────────┬────────────┘
             │
             │ belongs to
             ▼
┌─────────────────────────┐
│         Asset           │
│                         │
│ product                 │
│ seller                  │
│ invoice_number          │
│ order_number            │
│ purchase_date           │
│ total_amount            │
│ warranty_months         │
│ warranty_expiry         │
│ warranty_status         │
└─────────────────────────┘
```

This creates a useful distinction:

**Document = what was uploaded**

**Asset = what the system understands about the purchase**

---

# End-to-End Workflow

### 01 — Upload

The user uploads a receipt through the application.

```http
POST /api/receipts/upload
```

### 02 — Understand

The backend processes the uploaded document using visual processing and OCR fallback.

### 03 — Extract

Purchase information is extracted into structured fields.

### 04 — Calculate

Warranty information is processed and the appropriate purchase date is used for warranty calculations.

### 05 — Store

The purchase becomes a persistent `Asset`, while the source file is represented as a `Document`.

### 06 — Search

Assets can be searched using the asset/search layer.

```http
GET /api/assets/search
```

### 07 — Ask

The assistant can use the stored purchase information to answer natural-language questions.

```text
"Which laptop did I buy?"
"When does my TV warranty expire?"
"Do I still have warranty coverage?"
```

---

# API Surface

WarrantyVault exposes a FastAPI backend with dedicated API layers.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/receipts/upload` | Upload a receipt |
| `POST` | `/api/assets/process` | Process an asset |
| `GET` | `/api/assets/search` | Search assets |
| `GET` | `/api/assets/` | Retrieve assets |
| `GET` | `/api/assets/{asset_id}/documents` | Retrieve asset documents |
| `GET` | `/api/assets/{asset_id}/documents/{document_type}` | Retrieve a specific document |
| `DELETE` | `/api/assets/{asset_id}` | Delete an asset |

Interactive API documentation is available through FastAPI's generated documentation when the backend is running.

---

# Architecture

```text
                         ┌──────────────────────┐
                         │      React UI        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         └──────────┬───────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
        Receipt API           Asset API           Assistant API
               │                    │                    │
               └────────────────────┼────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Service Layer     │
                         ├──────────────────────┤
                         │ Receipt Extraction   │
                         │ Vision Processing     │
                         │ OCR                   │
                         │ Warranty Extraction  │
                         │ Warranty Service      │
                         │ Asset Service         │
                         │ Claim Service         │
                         │ Semantic Search       │
                         │ Assistant Service     │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
            ┌──────────┐     ┌────────────┐    ┌────────────┐
            │  Ollama  │     │ PaddleOCR  │    │ Database   │
            │ Local LLM│     │ OCR        │    │ / Assets   │
            └──────────┘     └────────────┘    └────────────┘
```

---

# Project Structure

```text
WarrantyVault/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── assets.py
│   │   │   ├── assistant.py
│   │   │   └── receipts.py
│   │   │
│   │   ├── models/
│   │   │   ├── asset.py
│   │   │   └── document.py
│   │   │
│   │   ├── services/
│   │   │   ├── asset_repository.py
│   │   │   ├── asset_service.py
│   │   │   ├── assistant_service.py
│   │   │   ├── claim_service.py
│   │   │   ├── document_repository.py
│   │   │   ├── ocr_service.py
│   │   │   ├── receipt_extractor.py
│   │   │   ├── semantic_search_service.py
│   │   │   ├── vision_service.py
│   │   │   ├── warranty_extractor.py
│   │   │   └── warranty_service.py
│   │   │
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── create_tables.py
│   ├── requirements.txt
│   └── tests...
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   └── raw/
│       └── sample receipt images
│
├── .gitignore
└── README.md
```

---

# Technology Stack

### Backend

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **Pydantic / FastAPI schemas**
- Service + repository architecture

### AI / Document Intelligence

- **Ollama** — local LLM runtime
- **Vision processing** — receipt understanding
- **PaddleOCR** — OCR fallback
- **Semantic search** — natural-language retrieval

### Frontend

- **React**
- **Vite**
- JavaScript / JSX
- CSS

### Data Layer

- SQLAlchemy ORM
- Asset / Document relational model
- Persistent document metadata

---

# Engineering Highlights

## Layered Architecture

The application separates API routing from business logic and persistence.

```text
API
 ↓
Services
 ↓
Repositories
 ↓
Database
```

This keeps document processing, warranty logic, search and assistant functionality from becoming tightly coupled to HTTP endpoints.

---

## Fallback-Based Document Processing

Instead of assuming the first extraction method always succeeds:

```text
Primary Vision Path
        │
        ├── Success ──────► Structured Data
        │
        └── Failure
                │
                ▼
            PaddleOCR
                │
                ▼
        Structured Data
```

---

## Explicit Warranty Business Logic

Warranty information isn't simply stored as raw text.

The system maintains fields specifically for warranty reasoning:

```text
purchase_date
      +
warranty_months
      │
      ▼
warranty_expiry
      │
      ▼
warranty_status
```

The original invoice/order dates are retained separately from the purchase date used by the warranty calculation logic.

---

## Searchable Assets

Once receipt information has been converted into assets, the application can work with purchases as data rather than repeatedly processing the original document.

This enables:

```text
Natural-language query
        ↓
Semantic retrieval
        ↓
Relevant asset
        ↓
Useful answer
```

---

# What Makes WarrantyVault Interesting?

A receipt-management application is easy to describe.

The engineering challenge is much more interesting.

WarrantyVault combines several different problems:

```text
Computer Vision
       +
OCR
       +
LLM-based extraction
       +
Business Rules
       +
Database Modeling
       +
Semantic Search
       +
Natural Language Interaction
```

Each individual component solves only one part of the problem.

The value comes from connecting them into a single pipeline.

---

# Example

### Input

A user uploads a receipt containing information such as:

```text
Seller:        Electronics Store
Product:       Laptop
Invoice No:    INV-XXXX
Order Date:    ...
Amount:        ...
Warranty:      ...
```

### WarrantyVault

```text
IMAGE
  ↓
VISION
  ↓
OCR FALLBACK
  ↓
LLM EXTRACTION
  ↓
STRUCTURED ASSET
  ↓
WARRANTY CALCULATION
  ↓
DATABASE
```

### User

> "Is my laptop still under warranty?"

### System

Instead of searching through the original image again, the assistant can work with the structured asset and warranty information already extracted by the system.

---

# Running Locally

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd WarrantyVault
```

---

## 2. Backend

Create and activate a Python virtual environment:

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

Create the database tables:

```powershell
python create_tables.py
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The FastAPI API will then be available locally.

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 3. Ollama

Install and run Ollama locally, then make sure the model required by the project's AI services is available in your Ollama environment.

Verify that Ollama is running before testing the AI-powered extraction or assistant functionality.

> The exact model configuration is determined by the project's backend configuration/code rather than being hard-coded in this README.

---

# 4. Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite will provide the local frontend URL in the terminal.

---

# Testing

The backend contains tests covering multiple parts of the system, including:

```text
Receipt extraction
OCR
Vision processing
Semantic search
Warranty extraction
Warranty service
Asset service
API end-to-end flow
```

The repository also contains dedicated test scripts for exercising individual services and the complete API workflow.

---

# End-to-End Test

The intended system flow can be summarized as:

```text
          UPLOAD
             │
             ▼
        ┌──────────┐
        │ Receipt  │
        └────┬─────┘
             │
             ▼
       Vision / OCR
             │
             ▼
      AI Extraction
             │
             ▼
      Warranty Logic
             │
             ▼
       Create Asset
             │
        ┌────┴────┐
        ▼         ▼
      Search   Assistant
        │         │
        └────┬────┘
             ▼
        User Answer
```

---

# Current API Flow

```text
POST /api/receipts/upload
             │
             ▼
POST /api/assets/process
             │
             ▼
        Asset Created
             │
       ┌─────┴─────┐
       ▼           ▼
GET /api/assets/   GET /api/assets/search
       │
       ▼
Documents
       │
       ▼
GET /api/assets/{asset_id}/documents
```

---

# Design Philosophy

WarrantyVault is built around three ideas:

### 1. Documents should become data

Don't leave useful information trapped inside images.

### 2. AI should participate in a pipeline

The LLM is not the entire application.

It is one component inside a larger document-intelligence system.

### 3. Structured data should power interaction

Once a purchase becomes an asset, the application can search it, reason about it and expose it to the assistant.

---

# The Bigger Picture

Today:

```text
Receipt
   ↓
Warranty information
```

The architecture opens the door to much more:

```text
                    Digital Purchase History
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
           Warranty        Assets         Documents
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                       Semantic Search
                              │
                              ▼
                         AI Assistant
```

The long-term idea is not simply to build another receipt scanner.

It is to create a **machine-readable layer around the purchases people already own**.

---

# Project Status

WarrantyVault currently includes:

- Receipt upload workflow
- Vision-based receipt processing
- PaddleOCR fallback
- Structured receipt extraction
- Warranty extraction and calculation
- Asset and document persistence
- Asset search
- Semantic search service
- AI assistant layer
- Ollama local LLM integration
- React frontend
- FastAPI backend
- End-to-end API testing

---

<div align="center">

## WarrantyVault

**Receipts go in.  
Structured purchase intelligence comes out.**

```text
UPLOAD  →  UNDERSTAND  →  EXTRACT  →  STORE  →  SEARCH  →  ASK
```

Built as an end-to-end AI + backend + frontend engineering project.

</div>
