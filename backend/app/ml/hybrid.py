"""Hybrid Recommender combining collaborative and content-based filtering."""

import logging
from typing import Optional

from app.config import settings
from app.ml.collaborative import CollaborativeRecommender
from app.ml.content_based import ContentBasedRecommender

logger = logging.getLogger(__name__)


class HybridRecommender:
    """Weighted hybrid recommender with cold-start fallback logic."""

    def __init__(
        self,
        content_recommender: ContentBasedRecommender,
        collaborative_recommender: CollaborativeRecommender,
        collaborative_weight: float = 0.6,
        content_weight: float = 0.4,
    ) -> None:
        self.content = content_recommender
        self.collaborative = collaborative_recommender
        self.collab_weight = collaborative_weight
        self.content_weight = content_weight

    def get_recommendations(
        self,
        user_id: int,
        liked_movie_ids: list[int],
        top_n: int = 20,
        exclude_ids: Optional[set[int]] = None,
    ) -> list[dict]:
        """Get hybrid recommendations for a user.

        Strategy:
        - If user has enough ratings and collab model is fitted → hybrid blend
        - If user has few ratings → content-based only (cold-start)
        - If no data available → return empty (caller handles popularity fallback)

        Returns list of dicts: {movie_id, score, method}
        """
        exclude = exclude_ids or set()
        has_enough_ratings = len(liked_movie_ids) >= settings.MIN_RATINGS_FOR_COLLABORATIVE
        collab_available = self.collaborative.is_fitted and has_enough_ratings
        content_available = self.content.is_fitted and len(liked_movie_ids) > 0

        if collab_available and content_available:
            return self._hybrid_blend(
                user_id, liked_movie_ids, top_n, exclude
            )
        elif content_available:
            return self._content_only(liked_movie_ids, top_n, exclude)
        elif collab_available:
            return self._collab_only(user_id, top_n, exclude)
        else:
            logger.info(f"No recommendations available for user {user_id} (cold start)")
            return []

    def _hybrid_blend(
        self,
        user_id: int,
        liked_movie_ids: list[int],
        top_n: int,
        exclude: set[int],
    ) -> list[dict]:
        """Blend collaborative and content-based scores."""
        # Get more candidates than needed for merging
        n_candidates = top_n * 3

        collab_recs = self.collaborative.get_user_recommendations(
            user_id, n_candidates, exclude
        )
        content_recs = self.content.get_user_recommendations(
            liked_movie_ids, n_candidates, exclude
        )

        # Normalize scores to [0, 1]
        collab_scores = self._normalize_scores(collab_recs)
        content_scores = self._normalize_scores(content_recs)

        # Merge scores
        all_movie_ids = set(collab_scores.keys()) | set(content_scores.keys())
        merged = []
        for mid in all_movie_ids:
            c_score = collab_scores.get(mid, 0.0)
            ct_score = content_scores.get(mid, 0.0)
            blended = self.collab_weight * c_score + self.content_weight * ct_score
            method = "hybrid"
            if mid not in collab_scores:
                method = "content"
            elif mid not in content_scores:
                method = "collaborative"
            merged.append({"movie_id": mid, "score": blended, "method": method})

        # Sort by blended score
        merged.sort(key=lambda x: x["score"], reverse=True)
        return merged[:top_n]

    def _content_only(
        self,
        liked_movie_ids: list[int],
        top_n: int,
        exclude: set[int],
    ) -> list[dict]:
        """Fallback to content-based only (cold start)."""
        recs = self.content.get_user_recommendations(liked_movie_ids, top_n, exclude)
        return [
            {"movie_id": mid, "score": score, "method": "content"}
            for mid, score in recs
        ]

    def _collab_only(
        self,
        user_id: int,
        top_n: int,
        exclude: set[int],
    ) -> list[dict]:
        """Fallback to collaborative only."""
        recs = self.collaborative.get_user_recommendations(user_id, top_n, exclude)
        return [
            {"movie_id": mid, "score": score, "method": "collaborative"}
            for mid, score in recs
        ]

    @staticmethod
    def _normalize_scores(recs: list[tuple[int, float]]) -> dict[int, float]:
        """Normalize recommendation scores to [0, 1] range."""
        if not recs:
            return {}
        scores = [s for _, s in recs]
        min_s, max_s = min(scores), max(scores)
        range_s = max_s - min_s if max_s != min_s else 1.0
        return {mid: (score - min_s) / range_s for mid, score in recs}
