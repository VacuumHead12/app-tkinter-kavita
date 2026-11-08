"""
Profile / My Activity Page for KAVITA Movie Recommendation System.
Displays personal statistics, Watched Movies, Favourites, and User Reviews & Ratings.
"""

import customtkinter as ctk
from ui.components import (
    MovieCard, StatCard, PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER_COLOR
)
from poster_manager import poster_manager
from data_loader import movie_db
import database


class ProfilePage(ctk.CTkScrollableFrame):
    def __init__(self, master, open_movie_callback, navigate_callback, **kwargs):
        super().__init__(
            master,
            fg_color=BG_MAIN,
            corner_radius=0,
            **kwargs
        )
        self.open_movie_callback = open_movie_callback
        self.navigate_callback = navigate_callback

        self.current_tab = "watched"

        self._build_ui()

    def _build_ui(self):
        # 1. Profile Header Banner
        banner = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            border_color="#F2DEC9",
            border_width=1,
            corner_radius=12
        )
        banner.pack(padx=24, pady=(16, 20), fill="x")

        b_inner = ctk.CTkFrame(banner, fg_color="transparent")
        b_inner.pack(padx=24, pady=18, fill="x")

        # Avatar & User Info
        user_row = ctk.CTkFrame(b_inner, fg_color="transparent")
        user_row.pack(fill="x", pady=(0, 16))

        avatar = ctk.CTkLabel(
            user_row,
            text="🎬",
            font=ctk.CTkFont(size=36),
            width=54,
            height=54,
            fg_color="#FFFFFF",
            corner_radius=27
        )
        avatar.pack(side="left", padx=(0, 14))

        info_col = ctk.CTkFrame(user_row, fg_color="transparent")
        info_col.pack(side="left")

        u_name = ctk.CTkLabel(
            info_col,
            text="Movie Enthusiast",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        u_name.pack(anchor="w")

        u_sub = ctk.CTkLabel(
            info_col,
            text="KAVITA Member  •  Every movie tells a story.",
            font=ctk.CTkFont(size=12),
            text_color=PRIMARY_ORANGE,
            anchor="w"
        )
        u_sub.pack(anchor="w")

        # 2. Stats Grid Row
        stats = database.get_user_stats()
        stats_row = ctk.CTkFrame(b_inner, fg_color="transparent")
        stats_row.pack(fill="x")

        s1 = StatCard(stats_row, icon="👁", title="Movies Watched", value=str(stats["watched_count"]))
        s1.pack(side="left", padx=(0, 12))

        s2 = StatCard(stats_row, icon="♥", title="Favourites", value=str(stats["favourites_count"]))
        s2.pack(side="left", padx=(0, 12))

        s3 = StatCard(stats_row, icon="📑", title="In Watchlist", value=str(stats["watchlist_count"]))
        s3.pack(side="left", padx=(0, 12))

        avg_str = f"{stats['average_rating']:.1f}" if stats["average_rating"] > 0 else "—"
        s4 = StatCard(stats_row, icon="⭐", title="Average Rating", value=avg_str)
        s4.pack(side="left", padx=(0, 12))

        s5 = StatCard(stats_row, icon="✍", title="Reviews Written", value=str(stats["review_count"]))
        s5.pack(side="left")

        # 3. Segmented Tab Selector
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.pack(padx=24, pady=(10, 14), fill="x")

        self.tab_watched_btn = ctk.CTkButton(
            tab_bar,
            text=f"👁 Watched Movies ({stats['watched_count']})",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            corner_radius=6,
            height=32,
            command=lambda: self._switch_tab("watched")
        )
        self.tab_watched_btn.pack(side="left", padx=(0, 8))

        self.tab_fav_btn = ctk.CTkButton(
            tab_bar,
            text=f"♥ Favourites ({stats['favourites_count']})",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FFFFFF",
            hover_color=BG_SECONDARY,
            text_color=TEXT_PRIMARY,
            border_color="#E0D2C7",
            border_width=1,
            corner_radius=6,
            height=32,
            command=lambda: self._switch_tab("favourites")
        )
        self.tab_fav_btn.pack(side="left", padx=(0, 8))

        self.tab_rev_btn = ctk.CTkButton(
            tab_bar,
            text=f"✍ My Reviews ({stats['review_count']})",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FFFFFF",
            hover_color=BG_SECONDARY,
            text_color=TEXT_PRIMARY,
            border_color="#E0D2C7",
            border_width=1,
            corner_radius=6,
            height=32,
            command=lambda: self._switch_tab("reviews")
        )
        self.tab_rev_btn.pack(side="left")

        # 4. Tab Content Container
        self.tab_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_container.pack(padx=24, pady=(0, 24), fill="x")

        self.render_active_tab()

    def _switch_tab(self, tab_name: str):
        self.current_tab = tab_name

        # Update button highlights
        self.tab_watched_btn.configure(
            fg_color=PRIMARY_ORANGE if tab_name == "watched" else "#FFFFFF",
            text_color="#FFFFFF" if tab_name == "watched" else TEXT_PRIMARY,
            border_width=0 if tab_name == "watched" else 1
        )
        self.tab_fav_btn.configure(
            fg_color=PRIMARY_ORANGE if tab_name == "favourites" else "#FFFFFF",
            text_color="#FFFFFF" if tab_name == "favourites" else TEXT_PRIMARY,
            border_width=0 if tab_name == "favourites" else 1
        )
        self.tab_rev_btn.configure(
            fg_color=PRIMARY_ORANGE if tab_name == "reviews" else "#FFFFFF",
            text_color="#FFFFFF" if tab_name == "reviews" else TEXT_PRIMARY,
            border_width=0 if tab_name == "reviews" else 1
        )

        self.render_active_tab()

    def render_active_tab(self):
        for widget in self.tab_container.winfo_children():
            widget.destroy()

        if self.current_tab == "watched":
            self._render_movie_grid(
                database.get_watched(),
                empty_msg="You haven't marked any movies as watched yet.\nClick '👁 Mark as Watched' on any movie you've seen!"
            )
        elif self.current_tab == "favourites":
            self._render_movie_grid(
                database.get_favourites(),
                empty_msg="You don't have any favourites yet.\nTap '♥ Add to Favourites' to keep your best cinema moments here!"
            )
        elif self.current_tab == "reviews":
            self._render_reviews_list()

    def _render_movie_grid(self, movie_ids: list[int], empty_msg: str):
        movies = [movie_db.get_movie(mid) for mid in movie_ids if movie_db.get_movie(mid)]

        if not movies:
            empty_lbl = ctk.CTkLabel(
                self.tab_container,
                text=empty_msg,
                font=ctk.CTkFont(size=13),
                text_color=TEXT_SECONDARY,
                justify="center",
                pady=40
            )
            empty_lbl.pack(fill="x")
            return

        columns = 6
        current_row = None

        for idx, movie in enumerate(movies):
            if idx % columns == 0:
                current_row = ctk.CTkFrame(self.tab_container, fg_color="transparent")
                current_row.pack(fill="x", pady=6)

            card = MovieCard(
                current_row,
                movie=movie,
                on_click=self.open_movie_callback,
                width=135,
                height=202
            )
            card.pack(side="left", padx=(0, 14))

    def _render_reviews_list(self):
        reviews = database.get_all_reviews()

        if not reviews:
            empty_lbl = ctk.CTkLabel(
                self.tab_container,
                text="You haven't written any reviews yet.\nOpen any movie details page to leave your rating and review!",
                font=ctk.CTkFont(size=13),
                text_color=TEXT_SECONDARY,
                justify="center",
                pady=40
            )
            empty_lbl.pack(fill="x")
            return

        for rev in reviews:
            mid = rev["movie_id"]
            movie = movie_db.get_movie(mid)
            if not movie:
                continue

            card = ctk.CTkFrame(
                self.tab_container,
                fg_color=BG_CARD,
                border_color="#F2DEC9",
                border_width=1,
                corner_radius=8
            )
            card.pack(fill="x", pady=6)

            c_inner = ctk.CTkFrame(card, fg_color="transparent")
            c_inner.pack(padx=14, pady=12, fill="x")

            # Top Row: Title, Rating, Date, Delete
            top_row = ctk.CTkFrame(c_inner, fg_color="transparent")
            top_row.pack(fill="x", pady=(0, 4))

            title_btn = ctk.CTkButton(
                top_row,
                text=movie["title"],
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color=BG_SECONDARY,
                text_color=TEXT_PRIMARY,
                anchor="w",
                command=lambda m=movie: self.open_movie_callback(m)
            )
            title_btn.pack(side="left")

            rating_val = rev["rating"]
            rating_lbl = ctk.CTkLabel(
                top_row,
                text=f"★ {rating_val:.1f} / 10" if rating_val > 0 else "Unrated",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=PRIMARY_ORANGE
            )
            rating_lbl.pack(side="left", padx=12)

            date_lbl = ctk.CTkLabel(
                top_row,
                text=rev["updated_at"],
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            )
            date_lbl.pack(side="left", padx=8)

            del_btn = ctk.CTkButton(
                top_row,
                text="✕ Delete",
                font=ctk.CTkFont(size=11),
                fg_color="#FFFFFF",
                hover_color="#FFF0F0",
                text_color="#D9381E",
                border_color="#F0C0C0",
                border_width=1,
                width=65,
                height=24,
                corner_radius=4,
                command=lambda r_mid=mid: self._delete_review(r_mid)
            )
            del_btn.pack(side="right")

            # Review Text
            text_content = rev["review_text"] or "(No written review provided)"
            body_lbl = ctk.CTkLabel(
                c_inner,
                text=text_content,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_PRIMARY if rev["review_text"] else TEXT_MUTED,
                wraplength=800,
                justify="left",
                anchor="w"
            )
            body_lbl.pack(anchor="w", pady=(2, 0))

    def _delete_review(self, movie_id: int):
        database.delete_review(movie_id)
        self.render_active_tab()
