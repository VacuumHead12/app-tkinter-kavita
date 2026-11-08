"""
Recommendation module for KAVITA Movie Recommendation System.
Implements content-based filtering using TF-IDF Vectorization and Cosine Similarity
on Genres, Keywords, Overview, Cast, and Director metadata.
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from data_loader import movie_db

BASE_DIR = os.path.dirname(__file__)
TFIDF_CACHE_PKL = os.path.join(BASE_DIR, "tfidf_cache.pkl")


class RecommendationEngine:
    def __init__(self):
        self.tfidf_matrix = None
        self.id_to_idx: dict[int, int] = {}
        self.idx_to_id: list[int] = []
        self._initialize_model()

    def _initialize_model(self):
        """Loads cached TF-IDF matrix or computes from movie dataset."""
        need_compute = True

        if os.path.exists(TFIDF_CACHE_PKL):
            try:
                with open(TFIDF_CACHE_PKL, "rb") as f:
                    cache_data = pickle.load(f)
                    self.tfidf_matrix = cache_data["tfidf_matrix"]
                    self.id_to_idx = cache_data["id_to_idx"]
                    self.idx_to_id = cache_data["idx_to_id"]
                need_compute = False
            except Exception:
                need_compute = True

        if need_compute:
            self._compute_tfidf()
            try:
                with open(TFIDF_CACHE_PKL, "wb") as f:
                    pickle.dump({
                        "tfidf_matrix": self.tfidf_matrix,
                        "id_to_idx": self.id_to_idx,
                        "idx_to_id": self.idx_to_id
                    }, f)
            except Exception:
                pass

    def _clean_token(self, text: str) -> str:
        return text.lower().replace(" ", "")

    def _compute_tfidf(self):
        """Constructs weighted metadata soup and fits TF-IDF vectorizer."""
        df = movie_db.movies_df.copy()

        soups = []
        id_to_idx = {}
        idx_to_id = []

        for idx, row in enumerate(df.itertuples()):
            mid = row.id
            id_to_idx[mid] = idx
            idx_to_id.append(mid)

            overview = str(row.overview) if row.overview else ""

            # Clean and repeat tokens to balance weighting
            genres = [self._clean_token(g) for g in row.genres_list]
            keywords = [self._clean_token(k) for k in row.keywords_list]
            cast = [self._clean_token(c) for c in row.cast_list]
            director = [self._clean_token(row.director)] if row.director and row.director != "Unknown" else []

            # Weighting:
            # Director: 3x
            # Genres: 3x
            # Keywords: 2x
            # Cast: 2x
            # Overview: 1x
            soup_parts = [
                overview,
                " ".join(genres * 3),
                " ".join(keywords * 2),
                " ".join(cast * 2),
                " ".join(director * 3)
            ]
            soups.append(" ".join(soup_parts))

        tfidf = TfidfVectorizer(stop_words="english", min_df=2, max_features=12000)
        self.tfidf_matrix = tfidf.fit_transform(soups)
        self.id_to_idx = id_to_idx
        self.idx_to_id = idx_to_id

    def get_similar_movies(self, movie_id: int, top_n: int = 12) -> list[tuple[dict, float]]:
        """
        Calculates cosine similarity between target movie and all other movies.
        Returns: list of (movie_dict, similarity_score_float)
        """
        if movie_id not in self.id_to_idx:
            return []

        idx = self.id_to_idx[movie_id]
        # Compute cosine similarity for single row against full matrix
        sim_scores = linear_kernel(self.tfidf_matrix[idx:idx + 1], self.tfidf_matrix).flatten()

        # Sort indices descending
        best_indices = sim_scores.argsort()[::-1]

        results = []
        for i in best_indices:
            other_id = self.idx_to_id[i]
            if other_id == movie_id:
                continue  # Skip query movie itself

            movie = movie_db.get_movie(other_id)
            if movie:
                score = float(sim_scores[i])
                results.append((movie, round(score * 100, 1)))

            if len(results) >= top_n:
                break

        return results

    def get_user_recommendations(
        self,
        watched_ids: list[int],
        favourite_ids: list[int],
        top_n: int = 12
    ) -> list[tuple[dict, float, str]]:
        """
        Generates personalized recommendations based on user's watched and favourite movies.
        Returns: list of (movie_dict, score, reason_string)
        """
        # Exclude movies the user has already watched or favourited
        seen_ids = set(watched_ids) | set(favourite_ids)

        # If user has no history, provide top rated and popular curated picks
        if not seen_ids:
            curated = []
            for m in movie_db.top_rated_movies[:top_n]:
                curated.append((m, round(m["vote_average"] * 10, 1), "Top Rated Masterpiece"))
            return curated

        # Aggregate weighted similarity vectors
        aggregate_scores = np.zeros(self.tfidf_matrix.shape[0])
        seed_reasons = {}

        # Favourites have weight 2.0, Watched have weight 1.0
        weighted_seeds = []
        for mid in favourite_ids:
            if mid in self.id_to_idx:
                weighted_seeds.append((mid, 2.0))
        for mid in watched_ids:
            if mid in self.id_to_idx and mid not in favourite_ids:
                weighted_seeds.append((mid, 1.0))

        # Take up to 5 most recent seeds to keep recommendations focused
        recent_seeds = weighted_seeds[:5]

        for mid, weight in recent_seeds:
            idx = self.id_to_idx[mid]
            sim = linear_kernel(self.tfidf_matrix[idx:idx + 1], self.tfidf_matrix).flatten()
            aggregate_scores += sim * weight

            # Record reason for top matches
            seed_movie = movie_db.get_movie(mid)
            seed_title = seed_movie["title"] if seed_movie else "your taste"
            for top_i in sim.argsort()[-15:]:
                if top_i not in seed_reasons or sim[top_i] > seed_reasons[top_i][0]:
                    seed_reasons[top_i] = (sim[top_i], f"Because you liked {seed_title}")

        best_indices = aggregate_scores.argsort()[::-1]

        results = []
        for i in best_indices:
            mid = self.idx_to_id[i]
            if mid in seen_ids:
                continue

            movie = movie_db.get_movie(mid)
            if movie:
                score = round(float(aggregate_scores[i]) * 10, 1)
                reason = seed_reasons.get(i, (0, "Recommended based on your activity"))[1]
                results.append((movie, score, reason))

            if len(results) >= top_n:
                break

        return results


# Global singleton instance
recommender = RecommendationEngine()
