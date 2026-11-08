"""
Movie Details Page for KAVITA Movie Recommendation System.
Presents detailed movie information, cast, director, interactive Watchlist/Watched/Favourite toggles,
user review & rating submission, and content-based 'More Like This' recommendations.
"""

import customtkinter as ctk
from ui.components import (
    MovieCard, PillBadge, StarRatingWidget,
    PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER_COLOR
)
from poster_manager import poster_manager
from recommendation import recommender
import database


class MovieDetailsPage(ctk.CTkScrollableFrame):
    def __init__(self, master, movie: dict, on_back_callback, open_movie_callback, **kwargs):
        super().__init__(
            master,
            fg_color=BG_MAIN,
            corner_radius=0,
            **kwargs
        )
        self.movie = movie
        self.movie_id = movie["id"]
        self.on_back_callback = on_back_callback
        self.open_movie_callback = open_movie_callback

        self._build_ui()

    def _build_ui(self):
        # 1. Back Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(padx=24, pady=(14, 10), fill="x")

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Back to Movies",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=BG_SECONDARY,
            text_color=PRIMARY_ORANGE,
            border_color="#E0D2C7",
            border_width=1,
            width=130,
            height=30,
            corner_radius=6,
            command=self.on_back_callback
        )
        back_btn.pack(side="left")

        # 2. Main Details Hero Container (2 Columns)
        details_container = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_color="#F2DEC9",
            border_width=1,
            corner_radius=12
        )
        details_container.pack(padx=24, pady=(0, 20), fill="x")

        details_inner = ctk.CTkFrame(details_container, fg_color="transparent")
        details_inner.pack(padx=20, pady=20, fill="x")

        # Left Column: Large Poster & Action Buttons
        left_col = ctk.CTkFrame(details_inner, fg_color="transparent", width=240)
        left_col.pack(side="left", padx=(0, 24), anchor="n")

        self.poster_label = ctk.CTkLabel(left_col, text="", corner_radius=8, fg_color=BG_SECONDARY)
        self.poster_label.pack(pady=(0, 14))
        self._load_large_poster()

        # Action Buttons on Left Column
        actions_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        actions_frame.pack(fill="x")

        # Watchlist Button
        self.is_watchlist = database.is_in_watchlist(self.movie_id)
        self.watchlist_btn = ctk.CTkButton(
            actions_frame,
            text="✓ In Watchlist" if self.is_watchlist else "+ Add to Watchlist",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE if self.is_watchlist else BG_SECONDARY,
            text_color="#FFFFFF" if self.is_watchlist else DARK_ORANGE,
            hover_color=DARK_ORANGE if self.is_watchlist else "#FFE6D5",
            border_color=PRIMARY_ORANGE,
            border_width=1,
            height=34,
            corner_radius=6,
            command=self._toggle_watchlist
        )
        self.watchlist_btn.pack(fill="x", pady=3)

        # Watched Button
        self.is_watched = database.is_watched(self.movie_id)
        self.watched_btn = ctk.CTkButton(
            actions_frame,
            text="✓ Watched" if self.is_watched else "👁 Mark as Watched",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE if self.is_watched else BG_SECONDARY,
            text_color="#FFFFFF" if self.is_watched else DARK_ORANGE,
            hover_color=DARK_ORANGE if self.is_watched else "#FFE6D5",
            border_color=PRIMARY_ORANGE,
            border_width=1,
            height=34,
            corner_radius=6,
            command=self._toggle_watched
        )
        self.watched_btn.pack(fill="x", pady=3)

        # Favourites Button
        self.is_favourite = database.is_favourite(self.movie_id)
        self.fav_btn = ctk.CTkButton(
            actions_frame,
            text="♥ In Favourites" if self.is_favourite else "♡ Add to Favourites",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE if self.is_favourite else BG_SECONDARY,
            text_color="#FFFFFF" if self.is_favourite else DARK_ORANGE,
            hover_color=DARK_ORANGE if self.is_favourite else "#FFE6D5",
            border_color=PRIMARY_ORANGE,
            border_width=1,
            height=34,
            corner_radius=6,
            command=self._toggle_favourite
        )
        self.fav_btn.pack(fill="x", pady=3)

        # Right Column: Movie Info & Review Area
        right_col = ctk.CTkFrame(details_inner, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)

        # Title
        title_lbl = ctk.CTkLabel(
            right_col,
            text=self.movie.get("title", "Untitled"),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=600
        )
        title_lbl.pack(anchor="w", pady=(0, 2))

        # Tagline (if any)
        tagline = self.movie.get("tagline", "")
        if tagline:
            tag_lbl = ctk.CTkLabel(
                right_col,
                text=f'"{tagline}"',
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color=TEXT_SECONDARY,
                anchor="w",
                wraplength=600
            )
            tag_lbl.pack(anchor="w", pady=(0, 8))

        # Metadata Row: Year • Runtime • Rating
        meta_row = ctk.CTkFrame(right_col, fg_color="transparent")
        meta_row.pack(anchor="w", pady=(0, 10))

        year = self.movie.get("release_year", 0)
        year_str = str(year) if year > 0 else "N/A"
        runtime_str = self.movie.get("runtime_formatted", "N/A")
        rating_val = self.movie.get("vote_average", 0.0)
        votes_val = self.movie.get("vote_count", 0)

        meta_info = f"📅 {year_str}    ⏱ {runtime_str}    ⭐ {rating_val:.1f} / 10 ({votes_val:,} votes)"
        meta_lbl = ctk.CTkLabel(
            meta_row,
            text=meta_info,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=PRIMARY_ORANGE
        )
        meta_lbl.pack(side="left")

        # Genres Pills Row
        genres_row = ctk.CTkFrame(right_col, fg_color="transparent")
        genres_row.pack(anchor="w", pady=(0, 14))

        genres = self.movie.get("genres_list", [])
        if genres:
            for g in genres:
                pill = PillBadge(genres_row, text=g)
                pill.pack(side="left", padx=(0, 8))
        else:
            PillBadge(genres_row, text="General").pack(side="left")

        # Synopsis / Overview Header & Text
        syn_hdr = ctk.CTkLabel(
            right_col,
            text="SYNOPSIS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        syn_hdr.pack(anchor="w", pady=(0, 2))

        syn_text = self.movie.get("overview", "No synopsis available.")
        overview_lbl = ctk.CTkLabel(
            right_col,
            text=syn_text,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            justify="left",
            wraplength=620,
            anchor="w"
        )
        overview_lbl.pack(anchor="w", pady=(0, 14))

        # Director & Cast
        credits_box = ctk.CTkFrame(right_col, fg_color=BG_SECONDARY, corner_radius=8, border_color="#F2DEC9", border_width=1)
        credits_box.pack(fill="x", pady=(0, 18))

        c_inner = ctk.CTkFrame(credits_box, fg_color="transparent")
        c_inner.pack(padx=14, pady=10, fill="x")

        director = self.movie.get("director", "Unknown")
        dir_lbl = ctk.CTkLabel(
            c_inner,
            text=f"Director: {director}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        dir_lbl.pack(anchor="w", pady=(0, 4))

        cast_str = self.movie.get("cast_str", "Unknown")
        cast_lbl = ctk.CTkLabel(
            c_inner,
            text=f"Cast: {cast_str}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w",
            wraplength=580,
            justify="left"
        )
        cast_lbl.pack(anchor="w")

        # 3. User Review and Rating Section
        review_frame = ctk.CTkFrame(right_col, fg_color="#FFFDFB", corner_radius=8, border_color="#F2DEC9", border_width=1)
        review_frame.pack(fill="x")

        r_inner = ctk.CTkFrame(review_frame, fg_color="transparent")
        r_inner.pack(padx=14, pady=12, fill="x")

        r_hdr = ctk.CTkLabel(
            r_inner,
            text="YOUR RATING & REVIEW",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=PRIMARY_ORANGE,
            anchor="w"
        )
        r_hdr.pack(anchor="w", pady=(0, 6))

        # Check existing review
        existing_rev = database.get_review(self.movie_id)
        initial_rating = existing_rev["rating"] if existing_rev else 0.0
        initial_text = existing_rev["review_text"] if existing_rev else ""

        self.rating_widget = StarRatingWidget(r_inner, initial_rating=initial_rating)
        self.rating_widget.pack(anchor="w", pady=(0, 8))

        self.review_box = ctk.CTkTextbox(
            r_inner,
            height=70,
            font=ctk.CTkFont(size=12),
            fg_color="#FFFFFF",
            border_color="#E0D2C7",
            border_width=1,
            corner_radius=6
        )
        self.review_box.pack(fill="x", pady=(0, 8))
        if initial_text:
            self.review_box.insert("0.0", initial_text)

        btn_row = ctk.CTkFrame(r_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        save_btn = ctk.CTkButton(
            btn_row,
            text="Save Review",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            width=100,
            height=30,
            corner_radius=6,
            command=self._save_review
        )
        save_btn.pack(side="left", padx=(0, 10))

        if existing_rev:
            del_btn = ctk.CTkButton(
                btn_row,
                text="Delete",
                font=ctk.CTkFont(size=11),
                fg_color="#FFFFFF",
                hover_color="#FFF0F0",
                text_color="#D9381E",
                border_color="#E8B4B4",
                border_width=1,
                width=70,
                height=30,
                corner_radius=6,
                command=self._delete_review
            )
            del_btn.pack(side="left", padx=(0, 10))

        self.review_status_lbl = ctk.CTkLabel(
            btn_row,
            text=f"Last updated: {existing_rev['updated_at']}" if existing_rev else "",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.review_status_lbl.pack(side="left", padx=10)

        # 4. 'More Like This' Content-Based Recommendations Section
        self._build_recommendations_section()

    def _load_large_poster(self):
        mid = self.movie.get("id", 0)
        p_path = self.movie.get("poster_path", "")
        title = self.movie.get("title", "")
        year = self.movie.get("release_year", 0)
        rating = self.movie.get("vote_average", 0.0)

        def on_image_ready(ctk_img):
            try:
                self.after(0, lambda: self.poster_label.configure(image=ctk_img))
            except Exception:
                pass

        ctk_img = poster_manager.get_poster(
            movie_id=mid,
            poster_path=p_path,
            title=title,
            year=year,
            rating=rating,
            width=220,
            height=330,
            callback=on_image_ready
        )
        self.poster_label.configure(image=ctk_img)

    def _toggle_watchlist(self):
        if self.is_watchlist:
            database.remove_from_watchlist(self.movie_id)
            self.is_watchlist = False
            self.watchlist_btn.configure(
                text="+ Add to Watchlist",
                fg_color=BG_SECONDARY,
                text_color=DARK_ORANGE,
                hover_color="#FFE6D5"
            )
        else:
            database.add_to_watchlist(self.movie_id)
            self.is_watchlist = True
            self.watchlist_btn.configure(
                text="✓ In Watchlist",
                fg_color=PRIMARY_ORANGE,
                text_color="#FFFFFF",
                hover_color=DARK_ORANGE
            )

    def _toggle_watched(self):
        if self.is_watched:
            database.remove_from_watched(self.movie_id)
            self.is_watched = False
            self.watched_btn.configure(
                text="👁 Mark as Watched",
                fg_color=BG_SECONDARY,
                text_color=DARK_ORANGE,
                hover_color="#FFE6D5"
            )
        else:
            database.add_to_watched(self.movie_id)
            self.is_watched = True
            self.watched_btn.configure(
                text="✓ Watched",
                fg_color=PRIMARY_ORANGE,
                text_color="#FFFFFF",
                hover_color=DARK_ORANGE
            )

    def _toggle_favourite(self):
        if self.is_favourite:
            database.remove_from_favourites(self.movie_id)
            self.is_favourite = False
            self.fav_btn.configure(
                text="♡ Add to Favourites",
                fg_color=BG_SECONDARY,
                text_color=DARK_ORANGE,
                hover_color="#FFE6D5"
            )
        else:
            database.add_to_favourites(self.movie_id)
            self.is_favourite = True
            self.fav_btn.configure(
                text="♥ In Favourites",
                fg_color=PRIMARY_ORANGE,
                text_color="#FFFFFF",
                hover_color=DARK_ORANGE
            )

    def _save_review(self):
        rating = self.rating_widget.get_rating()
        text = self.review_box.get("0.0", "end").strip()

        if rating <= 0 and not text:
            self.review_status_lbl.configure(text="Please select a rating or write a review.")
            return

        database.save_review(self.movie_id, rating, text)
        self.review_status_lbl.configure(text="✓ Review and rating saved successfully!")

        # Also automatically mark as watched when rated/reviewed
        if not self.is_watched:
            database.add_to_watched(self.movie_id)
            self.is_watched = True
            self.watched_btn.configure(
                text="✓ Watched",
                fg_color=PRIMARY_ORANGE,
                text_color="#FFFFFF",
                hover_color=DARK_ORANGE
            )

    def _delete_review(self):
        database.delete_review(self.movie_id)
        self.review_box.delete("0.0", "end")
        self.rating_widget.set_rating(0)
        self.review_status_lbl.configure(text="Review removed.")

    def _build_recommendations_section(self):
        rec_frame = ctk.CTkFrame(self, fg_color="transparent")
        rec_frame.pack(padx=24, pady=(0, 24), fill="x")

        hdr = ctk.CTkLabel(
            rec_frame,
            text=f"✨ More Like '{self.movie.get('title', '')}'",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        hdr.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(
            rec_frame,
            text="Content-based recommendations generated using TF-IDF and Cosine Similarity on genre, plot, director, and cast",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        sub.pack(anchor="w", pady=(0, 12))

        similar_movies = recommender.get_similar_movies(self.movie_id, top_n=6)

        if not similar_movies:
            no_rec_lbl = ctk.CTkLabel(
                rec_frame,
                text="No similar movies found.",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_SECONDARY
            )
            no_rec_lbl.pack(anchor="w")
            return

        cards_row = ctk.CTkFrame(rec_frame, fg_color="transparent")
        cards_row.pack(fill="x")

        for movie, score in similar_movies:
            card = MovieCard(
                cards_row,
                movie=movie,
                on_click=self.open_movie_callback,
                width=135,
                height=202
            )
            card.pack(side="left", padx=(0, 14))
