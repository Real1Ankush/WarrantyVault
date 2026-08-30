from backend.app.database import Base, engine

from backend.app.models.asset import Asset
from backend.app.models.document import Document


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")