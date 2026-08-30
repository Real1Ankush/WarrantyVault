"""Isolated API end-to-end test; it never writes to the live wallet."""
import os
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = tempfile.TemporaryDirectory(prefix="warranty-api-e2e-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(TEST_DIR.name) / 'wallet.sqlite3'}"
os.environ["UPLOAD_DIR"] = str(Path(TEST_DIR.name) / "uploads")
os.environ["SQL_ECHO"] = "false"

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from backend.app.api import assistant as assistant_api
from backend.app.api import assets as assets_api
from backend.app.api import receipts as receipts_api
from backend.app.database import Base, engine
from backend.app.main import app


class FakeVisionService:
    def extract_receipt(self, _image_path):
        return {
            "seller": "Test Seller",
            "invoice_number": "INV-E2E-001",
            "order_number": "ORD-E2E-001",
            "order_date": "2025-08-01",
            "invoice_date": "2025-08-01",
            "purchase_date": "2025-08-01",
            "product": "Test Laptop",
            "product_id": "TEST-LAPTOP-1",
            "quantity": 1,
            "total_amount": 999.0,
        }


class FakeOCRService:
    def extract_text(self, _image_path):
        return [{"text": "12 months warranty", "confidence": 1.0, "box": None}]


class FakeAssistantService:
    def process_query(self, query, assets):
        asset = assets[0]
        return {
            "status": "matched",
            "message": "Matched test asset.",
            "query": query,
            "asset": {"id": asset.id},
            "retrieval": {"method": "test-double"},
        }


class ApiEndToEndTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def get_test_db():
            db = cls.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[assets_api.get_db] = get_test_db
        app.dependency_overrides[assistant_api.get_db] = get_test_db
        fake_vision = FakeVisionService()
        receipts_api.vision_service = fake_vision
        assets_api.vision_service = fake_vision
        assets_api.ocr_service = FakeOCRService()
        assistant_api.assistant_service = FakeAssistantService()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        engine.dispose()
        TEST_DIR.cleanup()

    def test_complete_wallet_flow(self):
        receipt = ("receipt.jpg", b"receipt-image", "image/jpeg")
        warranty = ("warranty.png", b"warranty-image", "image/png")

        upload = self.client.post("/api/receipts/upload", files={"file": receipt})
        self.assertEqual(upload.status_code, 200)

        created = self.client.post(
            "/api/assets/process",
            files={"receipt": receipt, "warranty": warranty},
        )
        self.assertEqual(created.status_code, 200)
        payload = created.json()
        asset_id = payload["asset_id"]

        duplicate = self.client.post(
            "/api/assets/process",
            files={"receipt": receipt, "warranty": warranty},
        )
        self.assertEqual(duplicate.status_code, 200)
        self.assertTrue(duplicate.json()["already_exists"])
        self.assertEqual(duplicate.json()["asset_id"], asset_id)
        self.assertEqual(len(list(Path(os.environ["UPLOAD_DIR"]).iterdir())), 3)

        documents = self.client.get(f"/api/assets/{asset_id}/documents")
        self.assertEqual(documents.status_code, 200)
        self.assertEqual(documents.json()["count"], 2)
        self.assertEqual(self.client.get(f"/api/assets/{asset_id}/documents/receipt").status_code, 200)
        self.assertEqual(self.client.get(f"/api/assets/{asset_id}/documents/warranty").status_code, 200)

        search = self.client.get("/api/assets/search", params={"q": "Test Laptop"})
        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.json()["count"], 1)

        assistant = self.client.post(
            "/api/assistant/query",
            json={"query": "Test Laptop stopped working"},
        )
        self.assertEqual(assistant.status_code, 200)
        self.assertEqual(assistant.json()["status"], "matched")
        self.assertIn("claim", assistant.json())

        claim = self.client.get(f"/api/assistant/claim/{asset_id}")
        self.assertEqual(claim.status_code, 200)
        self.assertEqual(claim.json()["claim"]["documents"][1]["status"], "available")


if __name__ == "__main__":
    unittest.main(verbosity=2)
