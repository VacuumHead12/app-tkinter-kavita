"""
Explore Page for KAVITA Movie Recommendation System.
Features grid browsing, text search, genre filter, era filter, sorting, and pagination.
"""

import math
import customtkinter as ctk
from ui.components import (
    MovieCard, PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR
)
from data_loader import movie_db


class ExplorePage(ctk.CTkScrollableFrame):
    def __init__(self, master, open_movie_callback, **kwargs):
        super().__init__(
            master,
            fg_color=BG_MAIN,
            corner_radius=0,
            **kwargs
        )
        self.open_movie_callback = open_movie_callback

        self.current_page = 1
        self.per_page = 24
        self.query_var = ctk.StringVar(value="")
        self.genre_var = ctk.StringVar(value="All")
        self.era_var = ctk.StringVar(value="All")
        self.sort_var = ctk.StringVar(value="Most Popular")

        self._build_ui()
        self.apply_filters()

    def set_filters(self, query: str = "", genre: str = "All", sort_by: str = "Most Popular"):
        """Programmatically set filters from external actions."""
        if query:
            self.query_var.set(query)
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, query)
        if genre:
            self.genre_var.set(genre)
        if sort_by:
            self.sort_var.set(sort_by)
        self.current_page = 1
        self.apply_filters()

    def _build_ui(self):
        # 1. Filter Bar Container
        filter_bar = ctk.CTkFrame(
            self,
            fg_color=BG_SECONDARY,
            border_color="#F2DEC9",
            border_width=1,
            corner_radius=10
        )
        filter_bar.pack(padx=24, pady=(16, 14), fill="x")

        filter_inner = ctk.CTkFrame(filter_bar, fg_color="transparent")
        filter_inner.pack(padx=16, pady=12, fill="x")

        # Row 1: Search Entry & Controls
        r1 = ctk.CTkFrame(filter_inner, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 10))

        search_lbl = ctk.CTkLabel(
            r1,
            text="Search:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        search_lbl.pack(side="left", padx=(0, 8))

        self.search_entry = ctk.CTkEntry(
            r1,
            placeholder_text="Search by movie title, director, or cast...",
            textvariable=self.query_var,
            width=320,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#FFFFFF",
            border_color="#E8D1C0"
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._on_search_trigger())

        search_btn = ctk.CTkButton(
            r1,
            text="Search",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            width=75,
            height=32,
            corner_radius=6,
            command=self._on_search_trigger
        )
        search_btn.pack(side="left", padx=(0, 8))

        clear_btn = ctk.CTkButton(
            r1,
            text="Clear",
            font=ctk.CTkFont(size=12),
            fg_color="#FFFFFF",
            hover_color="#F5F5F5",
            text_color=TEXT_SECONDARY,
            border_color="#D8D8D8",
            border_width=1,
            width=60,
            height=32,
            corner_radius=6,
            command=self._on_clear_search
        )
        clear_btn.pack(side="left")

        # Row 2: Filter dropdowns (Genre, Era, Sort)
        r2 = ctk.CTkFrame(filter_inner, fg_color="transparent")
        r2.pack(fill="x")

        # Genre
        g_lbl = ctk.CTkLabel(r2, text="Genre:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        g_lbl.pack(side="left", padx=(0, 6))

        genre_options = ["All"] + movie_db.genres_list
        self.genre_menu = ctk.CTkOptionMenu(
            r2,
            values=genre_options,
            variable=self.genre_var,
            command=lambda _: self._on_filter_changed(),
            width=140,
            height=30,
            fg_color="#FFFFFF",
            button_color=PRIMARY_ORANGE,
            button_hover_color=DARK_ORANGE,
            text_color=TEXT_PRIMARY,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_fg_color="#FFFFFF"
        )
        self.genre_menu.pack(side="left", padx=(0, 16))

        # Era
        era_lbl = ctk.CTkLabel(r2, text="Release Era:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        era_lbl.pack(side="left", padx=(0, 6))

        era_options = ["All", "2010s", "2000s", "1990s", "1980s", "Classics (< 1980)"]
        self.era_menu = ctk.CTkOptionMenu(
            r2,
            values=era_options,
            variable=self.era_var,
            command=lambda _: self._on_filter_changed(),
            width=140,
            height=30,
            fg_color="#FFFFFF",
            button_color=PRIMARY_ORANGE,
            button_hover_color=DARK_ORANGE,
            text_color=TEXT_PRIMARY,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_fg_color="#FFFFFF"
        )
        self.era_menu.pack(side="left", padx=(0, 16))

        # Sort By
        sort_lbl = ctk.CTkLabel(r2, text="Sort By:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        sort_lbl.pack(side="left", padx=(0, 6))

        sort_options = ["Most Popular", "Highest Rated", "Release Date (Newest)", "Title (A-Z)"]
        self.sort_menu = ctk.CTkOptionMenu(
            r2,
            values=sort_options,
            variable=self.sort_var,
            command=lambda _: self._on_filter_changed(),
            width=170,
            height=30,
            fg_color="#FFFFFF",
            button_color=PRIMARY_ORANGE,
            button_hover_color=DARK_ORANGE,
            text_color=TEXT_PRIMARY,
            dropdown_text_color=TEXT_PRIMARY,
            dropdown_fg_color="#FFFFFF"
        )
        self.sort_menu.pack(side="left")

        # 2. Results Header
        self.status_label = ctk.CTkLabel(
            self,
            text="Showing movies...",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.status_label.pack(padx=26, pady=(0, 12), fill="x")

        # 3. Grid Container for Movie Cards
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(padx=24, fill="x")

        # 4. Pagination Footer
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(padx=24, pady=24, fill="x")

        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text="← Previous Page",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            width=130,
            height=32,
            corner_radius=6,
            command=self._prev_page
        )
        self.prev_btn.pack(side="left")

        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Page 1 of 1",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.page_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Next Page →",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            width=130,
            height=32,
            corner_radius=6,
            command=self._next_page
        )
        self.next_btn.pack(side="right")

    def _on_search_trigger(self):
        self.current_page = 1
        self.apply_filters()

    def _on_clear_search(self):
        self.search_entry.delete(0, "end")
        self.query_var.set("")
        self.genre_var.set("All")
        self.era_var.set("All")
        self.sort_var.set("Most Popular")
        self.current_page = 1
        self.apply_filters()

    def _on_filter_changed(self):
        self.current_page = 1
        self.apply_filters()

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.apply_filters()

    def _next_page(self):
        self.current_page += 1
        self.apply_filters()

    def apply_filters(self):
        # Clear existing cards
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        query = self.query_var.get().strip()
        genre = self.genre_var.get()
        era = self.era_var.get()
        sort_by = self.sort_var.get()

        movies, total = movie_db.search_movies(
            query=query,
            genre=genre,
            era=era,
            sort_by=sort_by,
            page=self.current_page,
            per_page=self.per_page
        )

        max_pages = max(1, math.ceil(total / self.per_page))
        self.current_page = min(self.current_page, max_pages)

        # Update status & pagination UI
        start_item = (self.current_page - 1) * self.per_page + 1 if total > 0 else 0
        end_item = min(self.current_page * self.per_page, total)
        self.status_label.configure(
            text=f"Showing {start_item}–{end_item} of {total:,} movies"
        )
        self.page_label.configure(text=f"Page {self.current_page} of {max_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < max_pages else "disabled")

        if not movies:
            empty_lbl = ctk.CTkLabel(
                self.grid_container,
                text="No movies found matching your criteria.\nTry adjusting your search or filters.",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_SECONDARY,
                justify="center",
                pady=40
            )
            empty_lbl.pack(fill="x")
            return

        # Arrange in a clean grid (6 columns per row)
        columns = 6
        current_row_frame = None

        for idx, movie in enumerate(movies):
            if idx % columns == 0:
                current_row_frame = ctk.CTkFrame(self.grid_container, fg_color="transparent")
                current_row_frame.pack(fill="x", pady=6)

            card = MovieCard(
                current_row_frame,
                movie=movie,
                on_click=self.open_movie_callback,
                width=135,
                height=202
            )
            card.pack(side="left", padx=(0, 14))
