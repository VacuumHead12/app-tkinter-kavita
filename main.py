"""
Main application entry point for KAVITA Movie Recommendation System.
Initializes the CustomTkinter desktop interface, top navigation header,
global search bar, and page routing.
"""

import customtkinter as ctk
from ui.components import (
    PRIMARY_ORANGE, DARK_ORANGE, BG_MAIN, BG_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR
)
from ui.home_page import HomePage
from ui.explore_page import ExplorePage
from ui.recommendations_page import RecommendationsPage
from ui.watchlist_page import WatchlistPage
from ui.profile_page import ProfilePage
from ui.movie_details import MovieDetailsPage
from data_loader import movie_db

# Configure CustomTkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")


class KavitaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KAVITA — Every movie tells a story.")
        self.geometry("1240x820")
        self.minsize(1040, 700)
        self.configure(fg_color=BG_MAIN)

        # Center window on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - 1240) // 2)
        y = max(0, (screen_h - 820) // 2)
        self.geometry(f"1240x820+{x}+{y}")

        self.current_page_name = "home"
        self.history = []
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self._build_header()

        # Content container
        self.content_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content_frame.pack(fill="both", expand=True)

        # Load Home page by default
        self.navigate_to("home")

    def _build_header(self):
        header = ctk.CTkFrame(
            self,
            fg_color=BG_MAIN,
            border_color="#F2DEC9",
            border_width=1,
            corner_radius=0,
            height=66
        )
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(padx=24, pady=12, fill="both", expand=True)

        # 1. Left: Brand & Tagline
        brand_frame = ctk.CTkFrame(h_inner, fg_color="transparent")
        brand_frame.pack(side="left")

        logo_btn = ctk.CTkButton(
            brand_frame,
            text="🎬 KAVITA",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            fg_color="transparent",
            hover_color=BG_SECONDARY,
            text_color=PRIMARY_ORANGE,
            corner_radius=6,
            height=36,
            command=lambda: self.navigate_to("home")
        )
        logo_btn.pack(side="left", padx=(0, 10))

        tagline_lbl = ctk.CTkLabel(
            brand_frame,
            text="Every movie tells a story.",
            font=ctk.CTkFont(family="Arial", size=12, slant="italic"),
            text_color=TEXT_SECONDARY
        )
        tagline_lbl.pack(side="left")

        # 2. Center: Global Search Bar
        center_search = ctk.CTkFrame(h_inner, fg_color="transparent")
        center_search.pack(side="left", padx=30, expand=True)

        self.global_search_var = ctk.StringVar()
        self.global_search_entry = ctk.CTkEntry(
            center_search,
            placeholder_text="Search 4,800+ movies by title, director, cast...",
            textvariable=self.global_search_var,
            width=360,
            height=34,
            font=ctk.CTkFont(size=12),
            fg_color="#FFFFFF",
            border_color="#E0D2C7",
            corner_radius=17
        )
        self.global_search_entry.pack(side="left", padx=(0, 6))
        self.global_search_entry.bind("<Return>", lambda e: self._on_global_search())

        search_btn = ctk.CTkButton(
            center_search,
            text="🔍",
            width=34,
            height=34,
            fg_color=PRIMARY_ORANGE,
            hover_color=DARK_ORANGE,
            text_color="#FFFFFF",
            corner_radius=17,
            command=self._on_global_search
        )
        search_btn.pack(side="left")

        # 3. Right: Nav Buttons
        nav_frame = ctk.CTkFrame(h_inner, fg_color="transparent")
        nav_frame.pack(side="right")

        nav_items = [
            ("home", "Home"),
            ("explore", "Explore"),
            ("recommendations", "Recommendations"),
            ("watchlist", "Watchlist"),
            ("profile", "Profile")
        ]

        for page_id, label in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                hover_color=BG_SECONDARY,
                text_color=TEXT_PRIMARY,
                corner_radius=16,
                height=32,
                command=lambda pid=page_id: self.navigate_to(pid)
            )
            btn.pack(side="left", padx=3)
            self.nav_buttons[page_id] = btn

    def _on_global_search(self):
        query = self.global_search_var.get().strip()
        if not query:
            return
        self.navigate_to("explore", {"query": query})

    def navigate_to(self, page_name: str, params: dict | None = None):
        """Routes to a top-level page with optional parameters."""
        if self.current_page_name != page_name:
            self.history.append((self.current_page_name, None))

        self.current_page_name = page_name
        self._update_nav_highlights(page_name)

        # Clear existing page content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if page_name == "home":
            page = HomePage(
                self.content_frame,
                open_movie_callback=self.open_movie_details,
                navigate_callback=self.navigate_to
            )
            page.pack(fill="both", expand=True)

        elif page_name == "explore":
            page = ExplorePage(
                self.content_frame,
                open_movie_callback=self.open_movie_details
            )
            page.pack(fill="both", expand=True)
            if params:
                page.set_filters(
                    query=params.get("query", ""),
                    genre=params.get("genre", "All"),
                    sort_by=params.get("sort_by", "Most Popular")
                )

        elif page_name == "recommendations":
            page = RecommendationsPage(
                self.content_frame,
                open_movie_callback=self.open_movie_details
            )
            page.pack(fill="both", expand=True)

        elif page_name == "watchlist":
            page = WatchlistPage(
                self.content_frame,
                open_movie_callback=self.open_movie_details,
                navigate_callback=self.navigate_to
            )
            page.pack(fill="both", expand=True)

        elif page_name == "profile":
            page = ProfilePage(
                self.content_frame,
                open_movie_callback=self.open_movie_details,
                navigate_callback=self.navigate_to
            )
            page.pack(fill="both", expand=True)

    def open_movie_details(self, movie: dict):
        """Opens detailed view for a selected movie."""
        self.history.append((self.current_page_name, None))
        self.current_page_name = "details"
        self._update_nav_highlights("")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        details_page = MovieDetailsPage(
            self.content_frame,
            movie=movie,
            on_back_callback=self._go_back,
            open_movie_callback=self.open_movie_details
        )
        details_page.pack(fill="both", expand=True)

    def _go_back(self):
        if self.history:
            prev_page, _ = self.history.pop()
            if prev_page == "details":
                prev_page = "home"
            self.navigate_to(prev_page or "home")
        else:
            self.navigate_to("home")

    def _update_nav_highlights(self, active_page: str):
        for pid, btn in self.nav_buttons.items():
            if pid == active_page:
                btn.configure(
                    fg_color=PRIMARY_ORANGE,
                    hover_color=DARK_ORANGE,
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=BG_SECONDARY,
                    text_color=TEXT_PRIMARY
                )


def main():
    app = KavitaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
