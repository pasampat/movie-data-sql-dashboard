"""
app.py

Full Movie Data SQL Dashboard using Streamlit.
- Sidebar filters for genre, min rating, and min votes
- Filtered movie table
- Average rating per year line chart
- Movie count per genre bar chart
"""

import streamlit as st
import pandas as pd
from sql_utils import run_query

st.set_page_config(page_title="🎬 Movie SQL Dashboard", layout="wide")

# ---- Title ----
st.title("🎬 Movie Data SQL Dashboard")
st.write("Explore movies by rating, popularity, and genre using a SQLite backend.")


# ---- Sidebar Filters ----
st.sidebar.header("Filters")

# 1. Genre Dropdown
genre_query = """
SELECT DISTINCT genres
FROM movies
WHERE genres IS NOT NULL
"""
genre_df = run_query(genre_query)

all_genres = set()
for g in genre_df["genres"]:
    for item in g.split("|"):
        all_genres.add(item.strip())

genre_list = ["All"] + sorted(list(all_genres))
selected_genre = st.sidebar.selectbox("Select Genre", genre_list)

# 2. Min Rating Slider
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 7.0, 0.1)

# 3. Min Votes Slider
min_votes = st.sidebar.slider("Minimum Votes", 0, 20000, 500, 100)


# ---- Helper Function for Filtered Movies ----
def get_filtered_movies(genre: str, min_rating: float, min_votes: int, limit: int = 50) -> pd.DataFrame:
    if genre == "All":
        query = f"""
        SELECT title, release_year, vote_average, vote_count, genres
        FROM movies
        WHERE vote_average >= {min_rating} AND vote_count >= {min_votes}
        ORDER BY vote_average DESC
        LIMIT {limit};
        """
    else:
        query = f"""
        SELECT title, release_year, vote_average, vote_count, genres
        FROM movies
        WHERE vote_average >= {min_rating}
          AND vote_count >= {min_votes}
          AND genres LIKE '%{genre}%'
        ORDER BY vote_average DESC
        LIMIT {limit};
        """
    return run_query(query)


# ---- Main Dashboard ----
st.subheader("🎥 Filtered Movies")
movies_df = get_filtered_movies(selected_genre, min_rating, min_votes)

if not movies_df.empty:
    st.dataframe(movies_df, use_container_width=True)
else:
    st.warning("No movies match your filters. Try lowering the thresholds.")


# ---- Chart 1: Average Rating per Year ----
st.subheader("📈 Average Rating Per Year")

rating_trend_query = f"""
SELECT release_year, ROUND(AVG(vote_average), 2) AS avg_rating
FROM movies
WHERE vote_average >= {min_rating} AND vote_count >= {min_votes}
GROUP BY release_year
ORDER BY release_year;
"""
rating_df = run_query(rating_trend_query)

if not rating_df.empty:
    st.line_chart(rating_df.set_index("release_year"))
else:
    st.info("Not enough data for the selected filters to plot ratings by year.")


# ---- Chart 2: Movie Count Per Genre ----
st.subheader("📊 Movie Count Per Genre (Top 10)")

genre_count_query = """
SELECT genres, COUNT(*) AS movie_count
FROM movies
WHERE genres IS NOT NULL
GROUP BY genres
ORDER BY movie_count DESC
LIMIT 10;
"""
genre_count_df = run_query(genre_count_query)

if not genre_count_df.empty:
    genre_count_df = genre_count_df.sort_values("movie_count", ascending=True)
    st.bar_chart(
        data=genre_count_df,
        x="genres",
        y="movie_count",
        use_container_width=True,
    )
else:
    st.info("No genre data available for the selected filters.")
