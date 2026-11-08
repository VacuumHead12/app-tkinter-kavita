"""
Data loader module for KAVITA Movie Recommendation System.
Loads, cleans, and indexes the TMDB 5000 Movies and Credits datasets.
Provides fast lookups, searches, and filtering.
"""

import os
import ast
import pickle
import pandas as pd
from database import get_cached_poster_path

BASE_DIR = os.path.dirname(__file__)
MOVIES_CSV = os.path.join(BASE_DIR, "tmdb_5000_movies.csv")
CREDITS_CSV = os.path.join(BASE_DIR, "tmdb_5000_credits.csv")
CACHE_PKL = os.path.join(BASE_DIR, "data_cache.pkl")


def safe_parse_json(val):
    if pd.isna(val) or not isinstance(val, str):
        return []
    try:
        return ast.literal_eval(val)
    except Exception:
        return []


def extract_names(items, key="name", limit=None):
    if not isinstance(items, list):
        return []
    res = [item[key] for item in items if isinstance(item, dict) and key in item]
    return res[:limit] if limit else res


def extract_director(crew):
    if not isinstance(crew, list):
        return "Unknown"
    for member in crew:
        if isinstance(member, dict) and member.get("job") == "Director":
            return member.get("name", "Unknown")
    return "Unknown"


def format_runtime(minutes):
    try:
        m = int(minutes)
        if m <= 0:
            return "N/A"
        hrs = m // 60
        mins = m % 60
        if hrs > 0 and mins > 0:
            return f"{hrs}h {mins}m"
        elif hrs > 0:
            return f"{hrs}h"
        else:
            return f"{mins}m"
    except Exception:
        return "N/A"


class MovieDatabase:
    """In-memory movie database providing fast search, filtering, and retrieval."""

    def __init__(self):
        self.movies_df: pd.DataFrame = None
        self.movie_map: dict[int, dict] = {}
        self.genres_list: list[str] = []
        self.popular_movies: list[dict] = []
        self.top_rated_movies: list[dict] = []
        self.recent_movies: list[dict] = []
        self._load_data()

    def _load_data(self):
        """Loads data from cache if available, or processes CSVs and creates cache."""
        need_rebuild = True

        if os.path.exists(CACHE_PKL):
            try:
                csv_mtime = max(os.path.getmtime(MOVIES_CSV), os.path.getmtime(CREDITS_CSV))
                pkl_mtime = os.path.getmtime(CACHE_PKL)
                if pkl_mtime > csv_mtime:
                    with open(CACHE_PKL, "rb") as f:
                        self.movies_df = pickle.load(f)
                    need_rebuild = False
            except Exception:
                need_rebuild = True

        if need_rebuild:
            self._process_csvs()
            try:
                with open(CACHE_PKL, "wb") as f:
                    pickle.dump(self.movies_df, f)
            except Exception:
                pass

        self._build_indices()

    def _process_csvs(self):
        """Parses CSV files, cleans columns, extracts JSON structures."""
        movies = pd.read_csv(MOVIES_CSV)
        credits = pd.read_csv(CREDITS_CSV)

        # Merge on ID
        df = movies.merge(credits, left_on="id", right_on="movie_id")

        # Standardize text fields
        df["title"] = df["title_x"].fillna(df["original_title"]).fillna("Untitled")
        df["overview"] = df["overview"].fillna("No synopsis available for this movie.")
        df["tagline"] = df["tagline"].fillna("")

        # Extract JSON fields
        parsed_genres = df["genres"].apply(safe_parse_json)
        df["genres_list"] = parsed_genres.apply(lambda x: extract_names(x))
        df["genres_str"] = df["genres_list"].apply(lambda l: ", ".join(l) if l else "General")

        parsed_keywords = df["keywords"].apply(safe_parse_json)
        df["keywords_list"] = parsed_keywords.apply(lambda x: extract_names(x, limit=6))

        parsed_cast = df["cast"].apply(safe_parse_json)
        df["cast_list"] = parsed_cast.apply(lambda x: extract_names(x, limit=5))
        df["cast_str"] = df["cast_list"].apply(lambda l: ", ".join(l) if l else "Unknown Cast")

        parsed_crew = df["crew"].apply(safe_parse_json)
        df["director"] = parsed_crew.apply(extract_director)

        # Release year parsing
        def get_year(val):
            if pd.isna(val) or not isinstance(val, str):
                return 0
            try:
                return int(val.split("-")[0])
            except Exception:
                return 0

        df["release_date"] = df["release_date"].fillna("")
        df["release_year"] = df["release_date"].apply(get_year)

        # Numeric fields
        df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0.0).round(1)
        df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)
        df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0.0)
        df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce").fillna(0).astype(int)
        df["runtime_formatted"] = df["runtime"].apply(format_runtime)

        # Poster path if column exists
        if "poster_path" in df.columns:
            df["poster_path"] = df["poster_path"].fillna("")
        else:
            df["poster_path"] = ""

        # Keep essential columns
        cols = [
            "id", "title", "original_title", "overview", "tagline",
            "release_date", "release_year", "vote_average", "vote_count",
            "popularity", "runtime", "runtime_formatted",
            "genres_list", "genres_str", "keywords_list",
            "cast_list", "cast_str", "director", "poster_path"
        ]
        self.movies_df = df[cols].copy()

    def _build_indices(self):
        """Builds in-memory dictionary mapping and genre lists for ultra-fast lookup."""
        records = self.movies_df.to_dict(orient="records")
        all_genres = set()

        for rec in records:
            mid = rec["id"]
            # Fill poster_path from database cache if empty
            if not rec.get("poster_path"):
                cached_path = get_cached_poster_path(mid)
                if cached_path:
                    rec["poster_path"] = cached_path

            self.movie_map[mid] = rec
            for g in rec.get("genres_list", []):
                if g:
                    all_genres.add(g)

        self.genres_list = sorted(list(all_genres))

        # Pre-cache Popular, Top Rated, and Recent collections
        # 1. Popular (highest popularity)
        pop_sorted = sorted(records, key=lambda x: x["popularity"], reverse=True)
        self.popular_movies = pop_sorted[:30]

        # 2. Top Rated (vote_count >= 1000 for verified high ratings)
        high_rated = [m for m in records if m["vote_count"] >= 1000]
        self.top_rated_movies = sorted(high_rated, key=lambda x: x["vote_average"], reverse=True)[:30]

        # 3. Recent releases (vote_count >= 100 to ensure quality, release_year >= 2012)
        recent_candidates = [m for m in records if m["release_year"] >= 2012 and m["vote_count"] >= 100]
        self.recent_movies = sorted(recent_candidates, key=lambda x: x["release_date"], reverse=True)[:30]

    def get_movie(self, movie_id: int) -> dict | None:
        """Returns movie dictionary by ID."""
        return self.movie_map.get(movie_id)

    def search_movies(
        self,
        query: str = "",
        genre: str = "All",
        era: str = "All",
        sort_by: str = "Most Popular",
        page: int = 1,
        per_page: int = 24
    ) -> tuple[list[dict], int]:
        """
        Filters and sorts movies based on criteria.
        Returns: (paged_movie_list, total_matches_count)
        """
        q = query.lower().strip()
        filtered = list(self.movie_map.values())

        # Text search across title, director, and top cast
        if q:
            filtered = [
                m for m in filtered
                if q in m["title"].lower()
                or q in m["director"].lower()
                or any(q in actor.lower() for actor in m["cast_list"])
            ]

        # Genre filter
        if genre and genre != "All":
            filtered = [m for m in filtered if genre in m["genres_list"]]

        # Era / Year filter
        if era and era != "All":
            if era == "2010s":
                filtered = [m for m in filtered if 2010 <= m["release_year"] <= 2019]
            elif era == "2000s":
                filtered = [m for m in filtered if 2000 <= m["release_year"] <= 2009]
            elif era == "1990s":
                filtered = [m for m in filtered if 1990 <= m["release_year"] <= 1999]
            elif era == "1980s":
                filtered = [m for m in filtered if 1980 <= m["release_year"] <= 1989]
            elif era == "Classics (< 1980)":
                filtered = [m for m in filtered if 0 < m["release_year"] < 1980]

        # Sorting
        if sort_by == "Most Popular":
            filtered.sort(key=lambda x: x["popularity"], reverse=True)
        elif sort_by == "Highest Rated":
            filtered.sort(key=lambda x: (x["vote_average"], x["vote_count"]), reverse=True)
        elif sort_by == "Release Date (Newest)":
            filtered.sort(key=lambda x: x["release_date"], reverse=True)
        elif sort_by == "Title (A-Z)":
            filtered.sort(key=lambda x: x["title"].lower())

        total_matches = len(filtered)

        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged = filtered[start_idx:end_idx]

        return paged, total_matches


# Global singleton instance
movie_db = MovieDatabase()
