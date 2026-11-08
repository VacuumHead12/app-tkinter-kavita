"""
Recommendations Page for KAVITA Movie Recommendation System.
Provides interactive content-based recommendation discovery based on any selected movie,
as well as personalized recommendations based on the user's personal activity.
"""

import customtkinter as ctk
from ui.components import (
    MovieCard, PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR
)
from data_loader import movie_db
from recommendation import recommender
import database


class RecommendationsPage(ctk.CTkScrollableFrame):
    def __init__(self, master, open_movie_callback, **kwargs):
        super().__init__(
            master,
            fg_color=BG_MAIN,
            corner_radius=0,
            **kwargs
        )
        self.open_movie_callback = open_movie_callback

        self.selected_movie_id = 19995  # Default to Avatar or popular movie
        self.search_var = ctk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        # 1. Header Banner
        banner = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            border_color="#F2DEC9",
            border_width=1,
            corner_radius=12
        )
        banner.pack(padx=24, pady=(16, 20), fill="x")

        banner_inner = ctk.CTkFrame(banner, fg_color="transparent")
        banner_inner.pack(padx=20, pady=18, fill="x")

        title = ctk.CTkLabel(
            banner_inner,
            text="✨ Content-Based Recommendation Engine",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title.pack(anchor="w", pady=(0, 4))

        subtitle = ctk.CTkLabel(
            banner_inner,
            text="Powered by TF-IDF Vectorization and Cosine Similarity over genres, keywords, synopsis, director, and cast.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 14))

        # Movie Picker Row
        picker_row = ctk.CTkFrame(banner_inner, fg_color="transparent")
        picker_row.pack(fill="x", pady=(0, 10))

        pick_lbl = ctk.CTkLabel(
            picker_row,
            text="Select a Seed Movie:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        pick_lbl.pack(side="left", padx=(0, 10))

        self.search_entry = ctk.CTkEntry(
            picker_row,
            placeholder_text="Type movie title (e.g. Inception, Interstellar, Pulp Fiction)...",
            textvariable=self.search_var,
            width=340,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#FFFFFF",
            border_color="#E0D2C7"
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._on_search_seed())

        find_btn = ctk.CTkButton(
            picker_row,
            text="Recommend Similar",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            width=150,
            height=32,
            corner_radius=6,
            command=self._on_search_seed
        )
        find_btn.pack(side="left")

        # Suggestion Chips Row
        chips_row = ctk.CTkFrame(banner_inner, fg_color="transparent")
        chips_row.pack(fill="x")

        c_lbl = ctk.CTkLabel(
            chips_row,
            text="Popular Seeds:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        c_lbl.pack(side="left", padx=(0, 8))

        popular_seeds = [
            ("Inception", 27205),
            ("Interstellar", 157336),
            ("The Dark Knight", 155),
            ("Pulp Fiction", 680),
            ("Fight Club", 550),
            ("The Matrix", 603),
            ("Avatar", 19995),
            ("Forrest Gump", 13)
        ]

        for s_title, s_id in popular_seeds:
            chip_btn = ctk.CTkButton(
                chips_row,
                text=s_title,
                font=ctk.CTkFont(size=11),
                fg_color="#FFFFFF",
                hover_color="#FFE6D5",
                text_color=DARK_ORANGE,
                border_color="#F0D0BC",
                border_width=1,
                corner_radius=12,
                height=24,
                command=lambda mid=s_id: self.select_seed_movie(mid)
            )
            chip_btn.pack(side="left", padx=(0, 6))

        # 2. Similar Movies Section
        self.similar_section = ctk.CTkFrame(self, fg_color="transparent")
        self.similar_section.pack(padx=24, pady=(0, 24), fill="x")

        self.similar_hdr = ctk.CTkLabel(
            self.similar_section,
            text="Movies Similar to Selected Title",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        self.similar_hdr.pack(anchor="w", pady=(0, 4))

        self.similar_sub = ctk.CTkLabel(
            self.similar_section,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.similar_sub.pack(anchor="w", pady=(0, 12))

        self.similar_grid = ctk.CTkFrame(self.similar_section, fg_color="transparent")
        self.similar_grid.pack(fill="x")

        # 3. Personalized For You Section (based on SQLite watched & favourites)
        self._build_personalized_section()

        # Load initial recommendations for default seed
        self.select_seed_movie(self.selected_movie_id)

    def _on_search_seed(self):
        query = self.search_var.get().strip().lower()
        if not query:
            return

        # Find first matching movie
        matches, _ = movie_db.search_movies(query=query, per_page=1)
        if matches:
            self.select_seed_movie(matches[0]["id"])
        else:
            self.similar_sub.configure(text=f"No movie found matching '{query}'. Try another title.")

    def select_seed_movie(self, movie_id: int):
        self.selected_movie_id = movie_id
        movie = movie_db.get_movie(movie_id)
        if not movie:
            return

        self.search_var.set(movie["title"])
        self.similar_hdr.configure(text=f"✨ Recommended if you enjoyed '{movie['title']}'")
        self.similar_sub.configure(
            text=f"Genre: {movie['genres_str']}  |  Director: {movie['director']}  |  Release: {movie['release_year']}"
        )

        for w in self.similar_grid.winfo_children():
            w.destroy()

        similar = recommender.get_similar_movies(movie_id, top_n=12)

        columns = 6
        current_row = None
        for idx, (rec_movie, score) in enumerate(similar):
            if idx % columns == 0:
                current_row = ctk.CTkFrame(self.similar_grid, fg_color="transparent")
                current_row.pack(fill="x", pady=6)

            card = MovieCard(
                current_row,
                movie=rec_movie,
                on_click=self.open_movie_callback,
                width=135,
                height=202
            )
            card.pack(side="left", padx=(0, 14))

    def _build_personalized_section(self):
        pers_frame = ctk.CTkFrame(self, fg_color="transparent")
        pers_frame.pack(padx=24, pady=(10, 24), fill="x")

        p_hdr = ctk.CTkLabel(
            pers_frame,
            text="🎯 Curated & Personalized for Your Taste",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        p_hdr.pack(anchor="w", pady=(0, 4))

        watched_ids = database.get_watched()
        favourite_ids = database.get_favourites()

        if watched_ids or favourite_ids:
            sub_text = f"Computed from your personal profile ({len(watched_ids)} watched, {len(favourite_ids)} favourites)"
        else:
            sub_text = "Curated top-tier picks. Mark movies as Watched or Favourites to personalize this feed!"

        p_sub = ctk.CTkLabel(
            pers_frame,
            text=sub_text,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        p_sub.pack(anchor="w", pady=(0, 12))

        user_recs = recommender.get_user_recommendations(watched_ids, favourite_ids, top_n=6)
        cards_row = ctk.CTkFrame(pers_frame, fg_color="transparent")
        cards_row.pack(fill="x")

        for movie, score, reason in user_recs:
            card = MovieCard(
                cards_row,
                movie=movie,
                on_click=self.open_movie_callback,
                width=135,
                height=202
            )
            card.pack(side="left", padx=(0, 14))
