import re

from backend.app.services.semantic_search_service import (
    SemanticSearchService,
)


class AssistantService:

    CATEGORY_KEYWORDS = {
        "headphone": [
            "headphone",
            "headphones",
            "headset",
            "earphone",
            "earphones",
            "earbud",
            "earbuds",
            "cans",
        ],
        "laptop": [
            "laptop",
            "notebook",
            "macbook",
        ],
        "phone": [
            "phone",
            "smartphone",
            "mobile",
            "iphone",
            "android",
        ],
        "television": [
            "tv",
            "television",
        ],
        "monitor": [
            "monitor",
            "display",
        ],
        "camera": [
            "camera",
            "dslr",
            "mirrorless",
        ],
        "tablet": [
            "tablet",
            "ipad",
        ],
    }

    STOP_WORDS = {
        "my",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "has",
        "have",
        "had",
        "stopped",
        "working",
        "broken",
        "broke",
        "not",
        "no",
        "please",
        "what",
        "which",
        "where",
        "show",
        "find",
        "me",
        "under",
        "warranty",
        "does",
        "do",
        "did",
        "and",
        "or",
        "of",
        "for",
        "to",
        "in",
        "on",
    }

    def __init__(self):
        self.semantic_search = SemanticSearchService()

    def process_query(
        self,
        query: str,
        assets: list,
    ):
        query = query.strip()

        if not query:
            return {
                "status": "invalid",
                "message": "Please enter a query.",
                "candidates": [],
            }

        query_lower = query.lower()

        category = self.detect_category(query_lower)

        # -------------------------------------------------
        # KEYWORD RETRIEVAL
        # -------------------------------------------------

        keyword_results = self.keyword_search(
            query_lower,
            category,
            assets,
        )

        keyword_scores = {
            asset.id: score
            for asset, score in keyword_results
        }

        # -------------------------------------------------
        # SEMANTIC RETRIEVAL
        # -------------------------------------------------

        semantic_assets = assets

        if category:
            category_assets = [
                asset
                for asset in assets
                if self.asset_matches_category(
                    asset,
                    category,
                )
            ]

            if category_assets:
                semantic_assets = category_assets

        semantic_results = self.semantic_search.search(
            query=query,
            assets=semantic_assets,
            top_k=len(semantic_assets),
            threshold=-1.0,
        )

        semantic_scores = {
            result["asset"].id: result["similarity"]
            for result in semantic_results
        }

        # -------------------------------------------------
        # COMBINE CANDIDATES
        # -------------------------------------------------

        candidate_ids = set(keyword_scores)
        candidate_ids.update(semantic_scores)

        if not candidate_ids:
            return {
                "status": "not_found",
                "message": (
                    "I couldn't find a matching product "
                    "in your digital asset wallet."
                ),
                "query": query,
                "category_detected": category,
                "candidates": [],
            }

        candidate_assets = {
            asset.id: asset
            for asset in assets
            if asset.id in candidate_ids
        }

        # -------------------------------------------------
        # NORMALIZE SCORES
        # -------------------------------------------------

        keyword_values = [
            keyword_scores.get(asset_id, 0)
            for asset_id in candidate_ids
        ]

        semantic_values = [
            semantic_scores.get(asset_id, -1)
            for asset_id in candidate_ids
        ]

        keyword_min = min(keyword_values)
        keyword_max = max(keyword_values)

        semantic_min = min(semantic_values)
        semantic_max = max(semantic_values)

        def normalize(
            value,
            minimum,
            maximum,
        ):
            if maximum == minimum:
                return 0.5

            return (
                (value - minimum)
                / (maximum - minimum)
            )

        ranked_candidates = []

        for asset_id in candidate_ids:

            keyword_score = keyword_scores.get(
                asset_id,
                keyword_min,
            )

            semantic_score = semantic_scores.get(
                asset_id,
                semantic_min,
            )

            keyword_normalized = normalize(
                keyword_score,
                keyword_min,
                keyword_max,
            )

            semantic_normalized = normalize(
                semantic_score,
                semantic_min,
                semantic_max,
            )

            hybrid_score = (
                0.55 * semantic_normalized
                + 0.45 * keyword_normalized
            )

            ranked_candidates.append(
                {
                    "asset": candidate_assets[asset_id],
                    "keyword_score": keyword_score,
                    "semantic_score": semantic_score,
                    "hybrid_score": hybrid_score,
                }
            )

        ranked_candidates.sort(
            key=lambda item: item["hybrid_score"],
            reverse=True,
        )

        # -------------------------------------------------
        # SINGLE CANDIDATE
        # -------------------------------------------------

        if len(ranked_candidates) == 1:

            asset = ranked_candidates[0]["asset"]

            return {
                "status": "matched",
                "message": self.build_single_asset_message(
                    asset,
                    query,
                ),
                "query": query,
                "category_detected": category,
                "asset": self.serialize_asset(asset),
                "retrieval": {
                    "method": "hybrid",
                    "keyword_score": ranked_candidates[0][
                        "keyword_score"
                    ],
                    "semantic_score": ranked_candidates[0][
                        "semantic_score"
                    ],
                },
            }

        # -------------------------------------------------
        # CHECK WHETHER QUERY IS GENERIC OR SPECIFIC
        # -------------------------------------------------

        query_words = set(
            re.findall(
                r"[a-z0-9]+",
                query_lower,
            )
        )

        useful_words = (
            query_words - self.STOP_WORDS
        )

        category_words = set()

        if category:
            category_words.update(
                self.CATEGORY_KEYWORDS.get(
                    category,
                    [],
                )
            )

        # These are words such as:
        # sony, boat, samsung, xm5, bassheads, etc.
        specific_words = (
            useful_words - category_words
        )

        # -------------------------------------------------
        # GENERIC CATEGORY QUERY
        # -------------------------------------------------

        # Examples:
        # "my headphones stopped working"
        # "my cans are broken"
        #
        # If multiple assets belong to this category and
        # there is no identifying product/brand clue,
        # NEVER select one based only on semantic score.

        if category and not specific_words:

            category_candidates = [
                item
                for item in ranked_candidates
                if self.asset_matches_category(
                    item["asset"],
                    category,
                )
            ]

            return {
                "status": "ambiguous",
                "message": (
                    f"I found {len(category_candidates)} "
                    f"{category} products in your wallet. "
                    "Which one are you referring to?"
                ),
                "query": query,
                "category_detected": category,
                "candidates": [
                    self.serialize_asset(
                        item["asset"]
                    )
                    for item in category_candidates
                ],
                "retrieval": {
                    "method": "hybrid",
                    "reason": "generic_category_query",
                },
            }

        # -------------------------------------------------
        # SPECIFIC QUERY
        # -------------------------------------------------

        top = ranked_candidates[0]
        second = ranked_candidates[1]

        score_difference = (
            top["hybrid_score"]
            - second["hybrid_score"]
        )

        # Specific information such as a brand/product name
        # is allowed to resolve ambiguity.
        if score_difference >= 0.15:

            asset = top["asset"]

            return {
                "status": "matched",
                "message": self.build_single_asset_message(
                    asset,
                    query,
                ),
                "query": query,
                "category_detected": category,
                "asset": self.serialize_asset(asset),
                "retrieval": {
                    "method": "hybrid",
                    "score_difference": score_difference,
                    "reason": "specific_query",
                },
            }

        # -------------------------------------------------
        # STILL AMBIGUOUS
        # -------------------------------------------------

        return {
            "status": "ambiguous",
            "message": (
                f"I found {len(ranked_candidates)} "
                "possible matches. Which product are "
                "you referring to?"
            ),
            "query": query,
            "category_detected": category,
            "candidates": [
                self.serialize_asset(
                    item["asset"]
                )
                for item in ranked_candidates
            ],
            "retrieval": {
                "method": "hybrid",
                "reason": "insufficient_specificity",
            },
        }

    # =====================================================
    # CATEGORY DETECTION
    # =====================================================

    def detect_category(self, query: str):

        words = set(
            re.findall(
                r"[a-z0-9]+",
                query.lower(),
            )
        )

        for category, keywords in (
            self.CATEGORY_KEYWORDS.items()
        ):

            if any(
                keyword in words
                for keyword in keywords
            ):
                return category

        return None

    # =====================================================
    # KEYWORD SEARCH
    # =====================================================

    def keyword_search(
        self,
        query: str,
        category: str | None,
        assets: list,
    ):

        query_words = set(
            re.findall(
                r"[a-z0-9]+",
                query.lower(),
            )
        )

        useful_words = (
            query_words - self.STOP_WORDS
        )

        scored = []

        for asset in assets:

            product = (
                asset.product or ""
            ).lower()

            seller = (
                asset.seller or ""
            ).lower()

            product_id = (
                asset.product_id or ""
            ).lower()

            score = 0

            if category:
                if self.asset_matches_category(
                    asset,
                    category,
                ):
                    score += 10

            for word in useful_words:

                if word in product:
                    score += 3

                if word in seller:
                    score += 2

                if word in product_id:
                    score += 2

            if score > 0:
                scored.append(
                    (asset, score)
                )

        scored.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scored

    # =====================================================
    # CATEGORY MATCHING
    # =====================================================

    def asset_matches_category(
        self,
        asset,
        category: str,
    ):

        product = (
            asset.product or ""
        ).lower()

        keywords = self.CATEGORY_KEYWORDS.get(
            category,
            [],
        )

        return any(
            keyword in product
            for keyword in keywords
        )

    # =====================================================
    # RESPONSE
    # =====================================================

    def build_single_asset_message(
        self,
        asset,
        query: str,
    ):

        product = (
            asset.product
            or "Unknown product"
        )

        warranty_status = (
            asset.warranty_status
            or "unknown"
        )

        if warranty_status == "active":

            warranty_message = (
                "The product is currently under "
                f"warranty until {asset.warranty_expiry}."
            )

        elif warranty_status == "expired":

            warranty_message = (
                "The recorded warranty expired on "
                f"{asset.warranty_expiry}."
            )

        else:

            warranty_message = (
                "I don't have verified warranty "
                "information for this product."
            )

        return (
            f"I found your {product}. "
            f"{warranty_message}"
        )

    # =====================================================
    # SERIALIZATION
    # =====================================================

    @staticmethod
    def serialize_asset(asset):

        return {
            "id": asset.id,
            "product": asset.product,
            "product_id": asset.product_id,
            "seller": asset.seller,
            "invoice_number": asset.invoice_number,
            "order_number": asset.order_number,
            "purchase_date": (
                asset.purchase_date.isoformat()
                if asset.purchase_date
                else None
            ),
            "total_amount": asset.total_amount,
            "warranty_months": asset.warranty_months,
            "warranty_source": asset.warranty_source,
            "warranty_expiry": (
                asset.warranty_expiry.isoformat()
                if asset.warranty_expiry
                else None
            ),
            "warranty_status": asset.warranty_status,
        }