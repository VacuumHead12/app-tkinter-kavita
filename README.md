# KAVITA — Movie Recommendation System
> *"Every movie tells a story."*

KAVITA is a desktop movie discovery and recommendation application inspired by Letterboxd, built with Python and CustomTkinter. It leverages the TMDB 5000 Movies and Credits dataset, real movie posters fetched via TMDB image services, an advanced content-based recommendation engine powered by TF-IDF and Cosine Similarity, and an SQLite database for personal watchlist, watched films, favourites, and reviews.

---

## 🎨 Design & Theme

- **Palette**:
  - Primary Orange: `#F07832`
  - Dark Orange: `#E56724`
  - Main Background: `#FFFFFF`
  - Secondary Background: `#FFF4EC`
  - Primary Text: `#252525`
  - Secondary Text: `#777777`
- **Aesthetics**: Clean, minimal, orange-and-white theme with subtle rounded corners, card borders, responsive poster grids, and typography inspired by Letterboxd.

---

## 🌟 Key Features

1. **Home Page**:
   - Hero banner with brand tagline: *"Every movie tells a story."*
   - Horizontal and grid sections for:
     - 🔥 **Popular This Week**
     - ⭐ **Top Rated Masterpieces** (verified 1,000+ votes)
     - ✨ **Recommended for You** (dynamically personalized to your profile)
     - 📅 **Recent Highlights**

2. **Explore Page**:
   - Search 4,800+ movies by title, director, or cast.
   - Filter by **Genre** (*Action, Adventure, Comedy, Drama, Sci-Fi, Thriller, etc.*).
   - Filter by **Release Era** (*2010s, 2000s, 1990s, 1980s, Classics*).
   - Sort by **Popularity**, **Rating**, **Release Date**, or **Title (A-Z)**.
   - Interactive movie cards and pagination controls (*Previous/Next*).

3. **Movie Details Page**:
   - High-resolution poster with clean aspect-ratio preservation.
   - Title, release year, runtime, star rating, and vote counts.
   - Genre badges and tagline.
   - Plot synopsis / overview.
   - Director and top cast members extracted from credits metadata.
   - Interactive toggle actions:
     - **+ Add to Watchlist** / **✓ In Watchlist**
     - **👁 Mark as Watched** / **✓ Watched**
     - **♡ Add to Favourites** / **♥ In Favourites**
   - User Rating & Review card (interactive 1–10 star selector, review text box, save/delete).
   - **More Like This**: Real-time content-based recommendations similar to the open movie.

4. **Recommendations Page**:
   - **Content-Based Algorithm**: Uses Scikit-learn's `TfidfVectorizer` and `linear_kernel` cosine similarity over a weighted metadata soup of **Genres (3x)**, **Director (3x)**, **Keywords (2x)**, **Cast (2x)**, and **Overview (1x)**.
   - Seed Movie Explorer: Search or choose from quick suggestion chips (*Inception, Interstellar, The Dark Knight, Pulp Fiction, Avatar, Fight Club, The Matrix, Forrest Gump*) to discover similar cinema.
   - **Personalized Feed**: Aggregates similarities across all movies in your personal watched and favourites list.

5. **Watchlist Page**:
   - Displays all movies saved in your personal queue.
   - Quick action buttons to mark as watched or remove from watchlist.
   - Direct click-through to movie details.
   - Empty state prompt with quick link to Explore.

6. **Profile / My Activity Page**:
   - Film enthusiast avatar and summary banner.
   - Statistics cards:
     - Total Movies Watched
     - Favourites Count
     - Watchlist Count
     - Average User Rating
     - Total Reviews Written
   - Segmented view tabs for **Watched Movies**, **Favourites**, and **My Reviews & Ratings**.

7. **Poster Management & Performance**:
   - Local storage in `movie_posters/{movie_id}.jpg`.
   - Downloads on demand from TMDB image service: `https://image.tmdb.org/t/p/w500/{poster_path}`.
   - Asynchronous background threading: network requests never freeze or stutter the Tkinter UI.
   - Clean, branded PIL placeholder cards if offline or while downloading.
   - In-memory `CTkImage` caching for instantaneous re-renders.

---

## 🗂 Project Structure

```
kavita/
├── main.py                  # Main application entry point & router
├── database.py              # SQLite storage (watchlist, watched, favourites, reviews)
├── data_loader.py           # Loads & indexes TMDB 5000 Movies & Credits
├── recommendation.py        # TF-IDF & Cosine Similarity recommendation engine
├── poster_manager.py        # TMDB poster downloader, PIL placeholder & image cache
├── movie_details.py         # Exports MovieDetailsPage
├── requirements.txt         # Project dependencies
├── tmdb_5000_movies.csv     # TMDB Movies dataset
├── tmdb_5000_credits.csv    # TMDB Credits dataset
├── movie_posters/           # Local folder storing downloaded posters ({id}.jpg)
├── ui/
│   ├── __init__.py
│   ├── components.py        # Reusable MovieCard, StarRatingWidget, PillBadge, StatCard
│   ├── home_page.py         # Home view
│   ├── explore_page.py      # Grid browsing, search, filter, and pagination
│   ├── movie_details.py     # Detailed movie view
│   ├── recommendations_page.py # Similarity engine & personalized picks
│   ├── watchlist_page.py    # Personal queue view
│   └── profile_page.py      # Profile statistics and activity journal
└── assets/                  # Application icons & visual resources
```

---

## 🚀 Getting Started

### 1. Requirements

Install required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launching KAVITA

Run the application:
```bash
python3 main.py
```
