"""
Poster manager module for KAVITA Movie Recommendation System.
Handles poster loading, downloading from TMDB image service,
aspect-ratio preserving resizing, in-memory caching, background threading,
and clean placeholder generation.
"""

import os
import requests
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
from database import get_cached_poster_path, cache_poster_path

BASE_DIR = os.path.dirname(__file__)
POSTER_DIR = os.path.join(BASE_DIR, "movie_posters")
os.makedirs(POSTER_DIR, exist_ok=True)

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


class PosterManager:
    def __init__(self):
        self._image_cache: dict[tuple[int, int, int], ctk.CTkImage] = {}
        self._placeholder_cache: dict[tuple[str, int, int], ctk.CTkImage] = {}
        self._in_flight: set[int] = set()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)

    def _get_local_file_path(self, movie_id: int) -> str:
        return os.path.join(POSTER_DIR, f"{movie_id}.jpg")

    def generate_placeholder(
        self,
        title: str,
        year: int = 0,
        rating: float = 0.0,
        width: int = 150,
        height: int = 225
    ) -> ctk.CTkImage:
        """Generates a clean, minimal placeholder card in orange and white palette."""
        cache_key = (f"{title}_{year}", width, height)
        if cache_key in self._placeholder_cache:
            return self._placeholder_cache[cache_key]

        img = Image.new("RGB", (width, height), color="#FFF4EC")
        draw = ImageDraw.Draw(img)

        # Subtle card border
        draw.rectangle([0, 0, width - 1, height - 1], outline="#F07832", width=1)

        # Center icon frame
        icon_box_h = int(height * 0.35)
        draw.rectangle([10, 10, width - 10, icon_box_h], fill="#FFE6D5", outline="#F07832", width=1)

        # Film emblem text
        try:
            emblem_text = "🎬\nKAVITA"
            draw.text((width // 2, icon_box_h // 2 + 5), emblem_text, fill="#F07832", anchor="mm", align="center")
        except Exception:
            pass

        # Movie title wrapped
        words = title.split()
        lines = []
        cur_line = []
        max_chars = max(8, width // 10)

        for w in words:
            if sum(len(x) for x in cur_line) + len(w) <= max_chars:
                cur_line.append(w)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [w]
            if len(lines) >= 3:
                break
        if cur_line and len(lines) < 3:
            lines.append(" ".join(cur_line))

        disp_title = "\n".join(lines[:3])
        draw.text((width // 2, int(height * 0.58)), disp_title, fill="#252525", anchor="mm", align="center")

        # Bottom badge: Year and Rating
        badge_y = height - 20
        badge_text = f"★ {rating:.1f}" if rating > 0 else (str(year) if year > 0 else "Movie")
        draw.rectangle([12, badge_y - 12, width - 12, badge_y + 8], fill="#FFFFFF", outline="#E56724", width=1)
        draw.text((width // 2, badge_y - 2), badge_text, fill="#E56724", anchor="mm")

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))
        self._placeholder_cache[cache_key] = ctk_img
        return ctk_img

    def _resize_image_aspect_ratio(self, pil_img: Image.Image, width: int, height: int) -> Image.Image:
        """Resizes and center-crops image to fill (width, height) without distortion."""
        target_ratio = width / height
        orig_w, orig_h = pil_img.size
        orig_ratio = orig_w / orig_h

        if orig_ratio > target_ratio:
            # Source is wider, crop horizontal edges
            new_w = int(orig_h * target_ratio)
            left = (orig_w - new_w) // 2
            pil_img = pil_img.crop((left, 0, left + new_w, orig_h))
        else:
            # Source is taller, crop vertical edges
            new_h = int(orig_w / target_ratio)
            top = (orig_h - new_h) // 2
            pil_img = pil_img.crop((0, top, orig_w, top + new_h))

        return pil_img.resize((width, height), Image.Resampling.LANCZOS)

    def _load_local_ctk_image(self, file_path: str, width: int, height: int) -> ctk.CTkImage | None:
        try:
            with Image.open(file_path) as raw_img:
                cropped = self._resize_image_aspect_ratio(raw_img.convert("RGB"), width, height)
                return ctk.CTkImage(light_image=cropped, dark_image=cropped, size=(width, height))
        except Exception:
            return None

    def get_poster(
        self,
        movie_id: int,
        poster_path: str = "",
        title: str = "Movie",
        year: int = 0,
        rating: float = 0.0,
        width: int = 150,
        height: int = 225,
        callback = None
    ) -> ctk.CTkImage:
        """
        Retrieves a CTkImage for a movie poster.
        If already cached in memory, returns immediately.
        If on disk, loads, caches, and returns immediately.
        If missing, returns a clean placeholder and triggers a background download.
        When the download finishes, invokes callback(ctk_image).
        """
        cache_key = (movie_id, width, height)
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        file_path = self._get_local_file_path(movie_id)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            ctk_img = self._load_local_ctk_image(file_path, width, height)
            if ctk_img:
                self._image_cache[cache_key] = ctk_img
                return ctk_img

        # Not on disk: generate placeholder first
        placeholder = self.generate_placeholder(title, year, rating, width, height)

        # Trigger background download if callback is given
        if callback and movie_id not in self._in_flight:
            self._in_flight.add(movie_id)
            self._executor.submit(
                self._download_and_notify,
                movie_id, poster_path, width, height, callback
            )

        return placeholder

    def _download_and_notify(
        self,
        movie_id: int,
        poster_path: str,
        width: int,
        height: int,
        callback
    ):
        try:
            # 1. Determine poster_path
            resolved_path = poster_path

            if not resolved_path:
                resolved_path = get_cached_poster_path(movie_id)

            if not resolved_path:
                # Query TMDB API for poster_path
                try:
                    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
                    res = requests.get(url, timeout=5)
                    if res.status_code == 200:
                        resolved_path = res.json().get("poster_path")
                        if resolved_path:
                            cache_poster_path(movie_id, resolved_path)
                except Exception:
                    resolved_path = None

            if not resolved_path:
                return

            # 2. Download from TMDB image CDN
            clean_path = resolved_path if resolved_path.startswith("/") else f"/{resolved_path}"
            image_url = f"{TMDB_IMAGE_BASE_URL}{clean_path}"

            res = requests.get(image_url, timeout=10)
            if res.status_code == 200 and len(res.content) > 1000:
                dest = self._get_local_file_path(movie_id)
                with open(dest, "wb") as f:
                    f.write(res.content)

                # 3. Create CTkImage and update cache
                ctk_img = self._load_local_ctk_image(dest, width, height)
                if ctk_img:
                    cache_key = (movie_id, width, height)
                    self._image_cache[cache_key] = ctk_img
                    if callback:
                        callback(ctk_img)
        except Exception:
            pass
        finally:
            self._in_flight.discard(movie_id)


# Global singleton instance
poster_manager = PosterManager()
