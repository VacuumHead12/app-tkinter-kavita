"""
Reusable UI components for KAVITA Movie Recommendation System.
"""

import customtkinter as ctk
from poster_manager import poster_manager

# Minimal Orange and White Color Theme
PRIMARY_ORANGE = "#F07832"
DARK_ORANGE = "#E56724"
BG_MAIN = "#FFFFFF"
BG_SECONDARY = "#FFF4EC"
BG_CARD = "#FFFFFF"
BG_CARD_HOVER = "#FFFBF8"
BORDER_COLOR = "#F2E2D6"
BORDER_ACTIVE = "#F07832"
TEXT_PRIMARY = "#252525"
TEXT_SECONDARY = "#777777"
TEXT_MUTED = "#999999"
STAR_GOLD = "#E56724"


class MovieCard(ctk.CTkFrame):
    """
    Interactive movie card with poster, title, year, rating badge,
    subtle hover styling, and async poster loading.
    """

    def __init__(
        self,
        master,
        movie: dict,
        on_click,
        width: int = 140,
        height: int = 210,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=BG_CARD,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=8,
            width=width + 12,
            **kwargs
        )
        self.movie = movie
        self.on_click = on_click
        self.poster_width = width
        self.poster_height = height

        # Poster label
        self.poster_label = ctk.CTkLabel(
            self,
            text="",
            corner_radius=6,
            fg_color=BG_SECONDARY
        )
        self.poster_label.pack(padx=6, pady=(6, 4))

        # Title
        title_text = movie.get("title", "Untitled")
        if len(title_text) > 28:
            title_text = title_text[:25] + "..."

        self.title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
            wraplength=width,
            justify="left",
            anchor="w"
        )
        self.title_label.pack(padx=8, pady=(0, 2), fill="x")

        # Meta row: Year & Rating
        meta_frame = ctk.CTkFrame(self, fg_color="transparent")
        meta_frame.pack(padx=8, pady=(0, 6), fill="x")

        year = movie.get("release_year", 0)
        year_str = str(year) if year > 0 else "—"
        self.year_label = ctk.CTkLabel(
            meta_frame,
            text=year_str,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY
        )
        self.year_label.pack(side="left")

        rating = movie.get("vote_average", 0.0)
        self.rating_label = ctk.CTkLabel(
            meta_frame,
            text=f"★ {rating:.1f}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=PRIMARY_ORANGE
        )
        self.rating_label.pack(side="right")

        # Initial poster load + async callback
        self._load_poster()

        # Bind click & hover events
        self._bind_events(self)
        self._bind_events(self.poster_label)
        self._bind_events(self.title_label)
        self._bind_events(self.year_label)
        self._bind_events(self.rating_label)
        self._bind_events(meta_frame)

    def _load_poster(self):
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
            width=self.poster_width,
            height=self.poster_height,
            callback=on_image_ready
        )
        self.poster_label.configure(image=ctk_img)

    def _bind_events(self, widget):
        widget.bind("<Button-1>", lambda e: self.on_click(self.movie))
        widget.bind("<Enter>", lambda e: self._on_enter())
        widget.bind("<Leave>", lambda e: self._on_leave())

    def _on_enter(self):
        self.configure(border_color=BORDER_ACTIVE, fg_color=BG_CARD_HOVER)

    def _on_leave(self):
        self.configure(border_color=BORDER_COLOR, fg_color=BG_CARD)


class PillBadge(ctk.CTkFrame):
    """Subtle badge pill for genres and metadata tags."""

    def __init__(self, master, text: str, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            border_color="#F4DAC7",
            border_width=1,
            corner_radius=12,
            **kwargs
        )
        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=DARK_ORANGE,
            padx=10,
            pady=3
        )
        label.pack()


class StatCard(ctk.CTkFrame):
    """Statistics card for profile overview."""

    def __init__(self, master, icon: str, title: str, value: str, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            border_color="#F2DEC9",
            border_width=1,
            corner_radius=10,
            width=160,
            height=100,
            **kwargs
        )
        self.pack_propagate(False)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(padx=12, pady=(10, 2), fill="x")

        icon_label = ctk.CTkLabel(
            top_frame,
            text=icon,
            font=ctk.CTkFont(size=18),
            text_color=PRIMARY_ORANGE
        )
        icon_label.pack(side="left")

        val_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=PRIMARY_ORANGE,
            anchor="w"
        )
        val_label.pack(padx=12, pady=(0, 2), fill="x")

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        title_label.pack(padx=12, fill="x")


class StarRatingWidget(ctk.CTkFrame):
    """Interactive 1 to 10 star rating selector."""

    def __init__(self, master, initial_rating: float = 0.0, on_rating_change=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.current_rating = initial_rating
        self.on_rating_change = on_rating_change
        self.star_buttons = []

        self.label = ctk.CTkLabel(
            self,
            text=f"Your Rating: {initial_rating:.1f}/10" if initial_rating > 0 else "Your Rating: Unrated",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.label.pack(anchor="w", pady=(0, 4))

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(anchor="w")

        for i in range(1, 11):
            btn = ctk.CTkButton(
                buttons_frame,
                text="★",
                width=26,
                height=26,
                font=ctk.CTkFont(size=14),
                fg_color=BG_SECONDARY if i <= initial_rating else "#F3F3F3",
                text_color=STAR_GOLD if i <= initial_rating else "#CCCCCC",
                hover_color="#FFE2D0",
                corner_radius=4,
                command=lambda val=i: self.set_rating(val)
            )
            btn.pack(side="left", padx=2)
            self.star_buttons.append(btn)

    def set_rating(self, val: int):
        self.current_rating = float(val)
        self.label.configure(text=f"Your Rating: {self.current_rating:.1f}/10")

        for i, btn in enumerate(self.star_buttons, 1):
            if i <= val:
                btn.configure(fg_color=BG_SECONDARY, text_color=STAR_GOLD)
            else:
                btn.configure(fg_color="#F3F3F3", text_color="#CCCCCC")

        if self.on_rating_change:
            self.on_rating_change(self.current_rating)

    def get_rating(self) -> float:
        return self.current_rating
