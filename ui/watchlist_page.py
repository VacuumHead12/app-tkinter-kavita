"""
Watchlist Page for KAVITA Movie Recommendation System.
Displays saved movies from SQLite watchlist, with quick remove, mark as watched,
and navigation to movie details.
"""

import customtkinter as ctk
from ui.components import (
    MovieCard, PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR
)
from data_loader import movie_db
import database


class WatchlistPage(ctk.CTkScrollableFrame):
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
        # 1. Header Bar
        hdr_frame = ctk.CTkFrame(self, fg_color="transparent")
        hdr_frame.pack(padx=24, pady=(16, 14), fill="x")

        title_lbl = ctk.CTkLabel(
            hdr_frame,
            text="📑 Your Watchlist",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.pack(anchor="w", pady=(0, 2))

        self.sub_lbl = ctk.CTkLabel(
            hdr_frame,
            text="Movies saved to your personal queue for upcoming film nights.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.sub_lbl.pack(anchor="w")

        # 2. Watchlist Grid Container
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(padx=24, pady=(0, 24), fill="x")

        self.load_watchlist()

    def load_watchlist(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        watchlist_ids = database.get_watchlist()
        movies = [movie_db.get_movie(mid) for mid in watchlist_ids if movie_db.get_movie(mid)]

        self.sub_lbl.configure(
            text=f"You have {len(movies)} movie{'s' if len(movies) != 1 else ''} saved in your queue."
        )

        if not movies:
            empty_frame = ctk.CTkFrame(self.grid_container, fg_color=BG_SECONDARY, corner_radius=12, border_color="#F2DEC9", border_width=1)
            empty_frame.pack(fill="x", pady=40, padx=40)

            e_inner = ctk.CTkFrame(empty_frame, fg_color="transparent")
            e_inner.pack(pady=40, padx=20)

            icon = ctk.CTkLabel(e_inner, text="📑", font=ctk.CTkFont(size=40))
            icon.pack(pady=(0, 10))

            t = ctk.CTkLabel(e_inner, text="Your Watchlist is Empty", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_PRIMARY)
            t.pack(pady=(0, 4))

            d = ctk.CTkLabel(
                e_inner,
                text="Discover cinema and tap '+ Add to Watchlist' on any movie to save it here for later.",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_SECONDARY
            )
            d.pack(pady=(0, 16))

            exp_btn = ctk.CTkButton(
                e_inner,
                text="Explore Movies →",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=PRIMARY_ORANGE,
                hover_color=DARK_ORANGE,
                text_color="#FFFFFF",
                corner_radius=6,
                command=lambda: self.navigate_callback("explore")
            )
            exp_btn.pack()
            return

        columns = 5
        current_row = None

        for idx, movie in enumerate(movies):
            if idx % columns == 0:
                current_row = ctk.CTkFrame(self.grid_container, fg_color="transparent")
                current_row.pack(fill="x", pady=8)

            card_wrapper = ctk.CTkFrame(current_row, fg_color="transparent")
            card_wrapper.pack(side="left", padx=(0, 16))

            card = MovieCard(
                card_wrapper,
                movie=movie,
                on_click=self.open_movie_callback,
                width=140,
                height=210
            )
            card.pack()

            # Actions below card: Quick Watched & Remove
            actions_bar = ctk.CTkFrame(card_wrapper, fg_color="transparent")
            actions_bar.pack(fill="x", pady=(4, 0))

            mark_watched_btn = ctk.CTkButton(
                actions_bar,
                text="✓ Watched",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=BG_SECONDARY,
                text_color=DARK_ORANGE,
                hover_color="#FFE6D5",
                border_color=PRIMARY_ORANGE,
                border_width=1,
                height=24,
                corner_radius=4,
                command=lambda mid=movie["id"]: self._mark_as_watched(mid)
            )
            mark_watched_btn.pack(side="left", expand=True, fill="x", padx=(0, 2))

            remove_btn = ctk.CTkButton(
                actions_bar,
                text="✕",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#FFFFFF",
                text_color="#D9381E",
                hover_color="#FFF0F0",
                border_color="#F0C0C0",
                border_width=1,
                width=24,
                height=24,
                corner_radius=4,
                command=lambda mid=movie["id"]: self._remove_from_watchlist(mid)
            )
            remove_btn.pack(side="right")

    def _mark_as_watched(self, movie_id: int):
        database.add_to_watched(movie_id)
        database.remove_from_watchlist(movie_id)
        self.load_watchlist()

    def _remove_from_watchlist(self, movie_id: int):
        database.remove_from_watchlist(movie_id)
        self.load_watchlist()
