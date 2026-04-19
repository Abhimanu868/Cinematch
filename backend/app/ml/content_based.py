"""Content-Based Filtering using TF-IDF and cosine similarity."""

import logging
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class ContentBasedRecommender:
    """Recommend movies based on content features (genres, overview, cast, keywords)."""

    def __init__(self) -> None:
        self.tfidf_matrix = None
        self.movie_ids: list[int] = []
        self.movie_id_to_idx: dict[int, int] = {}
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
        )
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    def _build_feature_string(self, row: pd.Series) -> str:
        """Combine all text features into a single feature string."""
        parts = []
        if pd.notna(row.get("genres")):
            # Weight genres more by repeating
            genres = str(row["genres"]).replace(",", " ")
            parts.append(genres + " " + genres)
        if pd.notna(row.get("overview")):
            parts.append(str(row["overview"]))
        if pd.notna(row.get("cast")):
            parts.append(str(row["cast"]).replace(",", " "))
        if pd.notna(row.get("director")):
            parts.append(str(row["director"]))
        if pd.notna(row.get("keywords")):
            parts.append(str(row["keywords"]).replace(",", " "))
        return " ".join(parts) if parts else ""

    def fit(self, movies_df: pd.DataFrame) -> None:
        """Build the TF-IDF matrix from movie features."""
        if movies_df.empty:
            logger.warning("Empty movies dataframe; cannot fit content model.")
            return

        logger.info(f"Fitting content-based model on {len(movies_df)} movies...")

        self.movie_ids = movies_df["id"].tolist()
        self.movie_id_to_idx = {mid: idx for idx, mid in enumerate(self.movie_ids)}

        # Build combined feature strings
        features = movies_df.apply(self._build_feature_string, axis=1)

        # Fit TF-IDF
        self.tfidf_matrix = self.vectorizer.fit_transform(features)
        self._is_fitted = True
        logger.info(f"Content-based model fitted. Matrix shape: {self.tfidf_matrix.shape}")

    def get_similar_movies(
        self, movie_id: int, top_n: int = 20, exclude_ids: Optional[set[int]] = None
    ) -> list[tuple[int, float]]:
        """Get top-N similar movies for a given movie using cosine similarity.

        Returns list of (movie_id, similarity_score) tuples.
        """
        if not self._is_fitted:
            logger.warning("Content model not fitted; returning empty results.")
            return []

        if movie_id not in self.movie_id_to_idx:
            return []

        idx = self.movie_id_to_idx[movie_id]
        movie_vector = self.tfidf_matrix[idx]

        # Compute similarity with all other movies
        similarities = cosine_similarity(movie_vector, self.tfidf_matrix).flatten()

        # Sort by similarity (descending), exclude self
        sim_indices = similarities.argsort()[::-1]

        exclude = exclude_ids or set()
        exclude.add(movie_id)

        results = []
        for i in sim_indices:
            mid = self.movie_ids[i]
            if mid not in exclude:
                results.append((mid, float(similarities[i])))
            if len(results) >= top_n:
                break

        return results

    def get_user_recommendations(
        self,
        liked_movie_ids: list[int],
        top_n: int = 20,
        exclude_ids: Optional[set[int]] = None,
    ) -> list[tuple[int, float]]:
        """Recommend movies based on a user's liked movies (content profile).

        Aggregates similarity scores from all liked movies.
        """
        if not self._is_fitted or not liked_movie_ids:
            return []

        exclude = exclude_ids or set()
        exclude.update(liked_movie_ids)

        # Build user profile as average of liked movie vectors
        valid_indices = [
            self.movie_id_to_idx[mid]
            for mid in liked_movie_ids
            if mid in self.movie_id_to_idx
        ]
        if not valid_indices:
            return []

        user_profile = self.tfidf_matrix[valid_indices].mean(axis=0)
        user_profile = np.asarray(user_profile)

        # Compute similarities
        similarities = cosine_similarity(user_profile, self.tfidf_matrix).flatten()
        sim_indices = similarities.argsort()[::-1]

        results = []
        for i in sim_indices:
            mid = self.movie_ids[i]
            if mid not in exclude:
                results.append((mid, float(similarities[i])))
            if len(results) >= top_n:
                break

        return results
