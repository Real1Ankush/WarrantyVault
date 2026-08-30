from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    String,
)

from backend.app.database import Base


class Asset(Base):

    __tablename__ = "assets"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product = Column(
        String(255),
        nullable=True,
    )

    product_id = Column(
        String(100),
        nullable=True,
    )

    seller = Column(
        String(255),
        nullable=True,
    )

    invoice_number = Column(
        String(100),
        nullable=True,
    )

    order_number = Column(
        String(100),
        nullable=True,
    )

    # Original dates from the invoice.
    order_date = Column(
        Date,
        nullable=True,
    )

    invoice_date = Column(
        Date,
        nullable=True,
    )

    # Date chosen by our business rule for
    # warranty calculations.
    purchase_date = Column(
        Date,
        nullable=True,
    )

    total_amount = Column(
        Float,
        nullable=True,
    )

    warranty_months = Column(
        Integer,
        nullable=True,
    )

    warranty_source = Column(
        String(100),
        nullable=True,
    )

    warranty_expiry = Column(
        Date,
        nullable=True,
    )

    warranty_status = Column(
        String(20),
        nullable=False,
        default="unknown",
    )