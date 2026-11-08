"""
Home Page for KAVITA Movie Recommendation System.
Displays hero banner, Popular, Top Rated, Personalized Recommendations, and Recent Releases.
"""

import customtkinter as ctk
from ui.components import (
    MovieCard, PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR
)
from data_loader import movie_db
from recommendation import recommender
import database


class HomePage(ctk.CTkScrollableFrame):
    def __init__(self, master, open_movie_callback, navigate_callback, **kwargs):
        super().__init__(
            master,
            fg_color=BG_MAIN,
            corner_radius=0,
            **kwargs
        )
        self.open_movie_callback = open_movie_callback
        self.navigate_callback = navigate_callback

        self._build_ui()

    def _build_ui(self):
        # 1. Hero / Welcome Banner
        hero_frame = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            border_color="#F4DAC7",
            border_width=1,
            corner_radius=12
        )
        hero_frame.pack(padx=24, pady=(16, 20), fill="x")

        hero_content = ctk.CTkFrame(hero_frame, fg_color="transparent")
        hero_content.pack(padx=24, pady=20, fill="x")

        tag_badge = ctk.CTkLabel(
            hero_content,
            text="🎬 MOVIE DISCOVERY & RECOMMENDATIONS",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=PRIMARY_ORANGE,
            anchor="w"
        )
        tag_badge.pack(anchor="w", pady=(0, 4))

        hero_title = ctk.CTkLabel(
            hero_content,
            text="Every movie tells a story.",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        hero_title.pack(anchor="w", pady=(0, 6))

        hero_subtitle = ctk.CTkLabel(
            hero_content,
            text="Discover cinema, explore personalized recommendations, and curate your personal film journal.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        hero_subtitle.pack(anchor="w", pady=(0, 14))

        btn_row = ctk.CTkFrame(hero_content, fg_color="transparent")
        btn_row.pack(anchor="w")

        explore_btn = ctk.CTkButton(
            btn_row,
            text="Browse All Movies →",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            corner_radius=6,
            height=32,
            command=lambda: self.navigate_callback("explore")
        )
        explore_btn.pack(side="left", padx=(0, 10))

        rec_btn = ctk.CTkButton(
            btn_row,
            text="Smart Recommendations",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FFFFFF",
            hover_color=BG_SECONDARY,
            text_color=DARK_ORANGE,
            border_color=PRIMARY_ORANGE,
            border_width=1,
            corner_radius=6,
            height=32,
            command=lambda: self.navigate_callback("recommendations")
        )
        rec_btn.pack(side="left")

        # 2. Section: Popular Movies
        self._create_section(
            title="🔥 Popular This Week",
            subtitle="The most discovered and talked about films right now",
            movies=movie_db.popular_movies[:6],
            explore_sort="Most Popular"
        )

        # 3. Section: Top Rated Classics
        self._create_section(
            title="⭐ Top Rated Masterpieces",
            subtitle="Critically acclaimed movies loved by audiences worldwide",
            movies=movie_db.top_rated_movies[:6],
            explore_sort="Highest Rated"
        )

        # 4. Section: Personalized Recommendations
        watched_ids = database.get_watched()
        favourite_ids = database.get_favourites()
        user_recs = recommender.get_user_recommendations(watched_ids, favourite_ids, top_n=6)
        rec_movies = [m[0] for m in user_recs]

        rec_title = "✨ Recommended For You"
        rec_subtitle = "Personalized picks tailored to your taste and activity"
        if not watched_ids and not favourite_ids:
            rec_subtitle = "Curated picks for you. Mark movies as watched or favourite for deeper personalization!"

        self._create_section(
            title=rec_title,
            subtitle=rec_subtitle,
            movies=rec_movies,
            explore_sort=None
        )

        # 5. Section: Recent Releases
        self._create_section(
            title="📅 Recent Highlights",
            subtitle="Recent cinema additions with strong community response",
            movies=movie_db.recent_movies[:6],
            explore_sort="Release Date (Newest)"
        )

    def _create_section(self, title: str, subtitle: str, movies: list[dict], explore_sort: str | None = None):
        section_frame = ctk.CTkFrame(self, fg_color="transparent")
        section_frame.pack(padx=24, pady=(10, 16), fill="x")

        # Section Header
        hdr_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        hdr_frame.pack(fill="x", pady=(0, 10))

        title_col = ctk.CTkFrame(hdr_frame, fg_color="transparent")
        title_col.pack(side="left")

        t_lbl = ctk.CTkLabel(
            title_col,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        t_lbl.pack(anchor="w")

        s_lbl = ctk.CTkLabel(
            title_col,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        s_lbl.pack(anchor="w")

        if explore_sort:
            view_all_btn = ctk.CTkButton(
                hdr_frame,
                text="View All →",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="transparent",
                hover_color=BG_SECONDARY,
                text_color=PRIMARY_ORANGE,
                width=70,
                height=26,
                command=lambda s=explore_sort: self.navigate_callback("explore", {"sort_by": s})
            )
            view_all_btn.pack(side="right")

        # Cards Grid Row
        cards_row = ctk.CTkFrame(section_frame, fg_color="transparent")
        cards_row.pack(fill="x")

        for idx, movie in enumerate(movies):
            card = MovieCard(
                cards_row,
                movie=movie,
                on_click=self.open_movie_callback,
                width=135,
                height=202
            )
            card.pack(side="left", padx=(0, 14), pady=4)
