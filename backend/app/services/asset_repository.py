from datetime import date

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from backend.app.models.asset import Asset


class AssetRepository:

    def create_asset(
        self,
        db: Session,
        asset_data: dict,
    ) -> Asset:

        asset = Asset(
            product=asset_data.get("product"),

            product_id=asset_data.get("product_id"),

            seller=asset_data.get("seller"),

            invoice_number=asset_data.get(
                "invoice_number"
            ),

            order_number=asset_data.get(
                "order_number"
            ),

            order_date=self._to_date(
                asset_data.get("order_date")
            ),

            invoice_date=self._to_date(
                asset_data.get("invoice_date")
            ),

            purchase_date=self._to_date(
                asset_data.get("purchase_date")
            ),

            total_amount=asset_data.get(
                "total_amount"
            ),

            warranty_months=asset_data.get(
                "warranty_months"
            ),

            warranty_source=asset_data.get(
                "warranty_source"
            ),

            warranty_expiry=self._to_date(
                asset_data.get("warranty_expiry")
            ),

            warranty_status=asset_data.get(
                "warranty_status",
                "unknown",
            ),
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    # =====================================================
    # DUPLICATE DETECTION
    # =====================================================

    def find_duplicate(
        self,
        db: Session,
        asset_data: dict,
    ):

        seller = asset_data.get("seller")
        invoice_number = asset_data.get(
            "invoice_number"
        )
        order_number = asset_data.get(
            "order_number"
        )
        product_id = asset_data.get(
            "product_id"
        )
        purchase_date = self._to_date(
            asset_data.get("purchase_date")
        )

        conditions = []

        # Strong identity #1:
        # seller + invoice number
        if seller and invoice_number:

            conditions.append(
                and_(
                    Asset.seller == seller,
                    Asset.invoice_number
                    == invoice_number,
                )
            )

        # Strong identity #2:
        # seller + order number
        if seller and order_number:

            conditions.append(
                and_(
                    Asset.seller == seller,
                    Asset.order_number
                    == order_number,
                )
            )

        # Strong identity #3:
        # invoice number + order number
        if invoice_number and order_number:

            conditions.append(
                and_(
                    Asset.invoice_number
                    == invoice_number,
                    Asset.order_number
                    == order_number,
                )
            )

        # Strong identity #4:
        # seller + product ID + purchase date
        if (
            seller
            and product_id
            and purchase_date
        ):

            conditions.append(
                and_(
                    Asset.seller == seller,
                    Asset.product_id
                    == product_id,
                    Asset.purchase_date
                    == purchase_date,
                )
            )

        # We don't have enough evidence to call it a duplicate.
        if not conditions:
            return None

        return (
            db.query(Asset)
            .filter(or_(*conditions))
            .order_by(Asset.id.asc())
            .first()
        )

    # =====================================================
    # GET ALL ASSETS
    # =====================================================

    def get_all_assets(
        self,
        db: Session,
    ):
        return db.query(Asset).all()

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_asset_by_id(
        self,
        db: Session,
        asset_id: int,
    ):

        return (
            db.query(Asset)
            .filter(
                Asset.id == asset_id
            )
            .first()
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search_assets(
        self,
        db: Session,
        query: str,
    ):

        search_term = (
            f"%{query.strip()}%"
        )

        return (
            db.query(Asset)
            .filter(
                (Asset.product.ilike(
                    search_term
                ))
                | (Asset.product_id.ilike(
                    search_term
                ))
                | (Asset.seller.ilike(
                    search_term
                ))
                | (Asset.invoice_number.ilike(
                    search_term
                ))
                | (Asset.order_number.ilike(
                    search_term
                ))
            )
            .all()
        )

    # =====================================================
    # DATE CONVERSION
    # =====================================================

    @staticmethod
    def _to_date(value):

        if value is None:
            return None

        if isinstance(value, date):
            return value

        return date.fromisoformat(value)