import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticSearchService:

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = None

    def _get_model(self):
        if self.model is None:
            print("Loading semantic search model...")
            self.model = SentenceTransformer(self.MODEL_NAME)
            print("Semantic search model loaded.")

        return self.model

    def build_asset_text(self, asset):
        """
        Convert an asset into the text representation that
        will be embedded for semantic search.
        """

        parts = [
            asset.product or "",
            asset.seller or "",
            asset.product_id or "",
        ]

        return " | ".join(
            part.strip()
            for part in parts
            if part.strip()
        )

    def encode_assets(self, assets):
        """
        Create one embedding for each asset.
        """

        texts = [
            self.build_asset_text(asset)
            for asset in assets
        ]

        model = self._get_model()

        if not texts:
            return np.empty(
                (
                    0,
                    model.get_sentence_embedding_dimension(),
                )
            )

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embeddings

    def search(
        self,
        query: str,
        assets: list,
        top_k: int = 5,
        threshold: float = 0.35,
    ):
        """
        Return assets ranked by semantic similarity.
        """

        if not query.strip() or not assets:
            return []

        model = self._get_model()

        query_embedding = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]

        asset_embeddings = self.encode_assets(assets)

        # Because both query and asset embeddings are normalized,
        # dot product is cosine similarity.
        scores = np.dot(
            asset_embeddings,
            query_embedding,
        )

        ranked_indices = np.argsort(
            scores
        )[::-1]

        results = []

        for index in ranked_indices[:top_k]:

            score = float(scores[index])

            if score < threshold:
                continue

            results.append({
                "asset": assets[index],
                "similarity": score,
            })

        return results
