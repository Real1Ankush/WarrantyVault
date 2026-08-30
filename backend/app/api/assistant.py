from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.services.asset_repository import AssetRepository
from backend.app.services.assistant_service import AssistantService
from backend.app.services.claim_service import ClaimService


router = APIRouter(
    prefix="/api/assistant",
    tags=["Assistant"],
)


class AssistantQuery(BaseModel):
    query: str


assistant_service = AssistantService()
asset_repository = AssetRepository()
claim_service = ClaimService()


@router.post("/query")
def assistant_query(
    request: AssistantQuery,
    db: Session = Depends(get_db),
):
    # Get all user's stored assets.
    assets = asset_repository.get_all_assets(db)

    # Run hybrid keyword + semantic retrieval.
    result = assistant_service.process_query(
        query=request.query,
        assets=assets,
    )

    # -----------------------------------------------------
    # UNIQUE MATCH
    # -----------------------------------------------------
    #
    # If exactly one asset was identified, automatically
    # prepare the warranty-claim information.
    #
    if result.get("status") == "matched":

        asset_data = result.get("asset")

        if asset_data is not None:

            asset_id = asset_data.get("id")

            asset = asset_repository.get_asset_by_id(
                db,
                asset_id,
            )

            if asset is not None:

                claim = claim_service.prepare_claim(
                    db,
                    asset,
                )

                result["claim"] = claim

    return result


@router.get("/claim/{asset_id}")
def prepare_claim(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = asset_repository.get_asset_by_id(
        db,
        asset_id,
    )

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found.",
        )

    claim = claim_service.prepare_claim(
        db,
        asset,
    )

    return {
        "asset_id": asset.id,
        "claim": claim,
    }