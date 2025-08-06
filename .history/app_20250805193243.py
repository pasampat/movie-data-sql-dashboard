"""
app.py

First version of the Movie Data SQL Dashboard using Streamlit.
- Sidebar filters for genre, min rating, and min votes
- Displays a filtered table of movies from SQLite
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

# Get all genres from DB
genre_query = """
SELECT DISTINCT genres
FROM movies
WHERE genres IS NOT NULL
"""
genre_df = run_query(genre_query)

# Flatten genres into unique individual options
all_genres = set()
for g in genre_df["genres"]:
    for item in g.split("|"):
        all_genres.add(item.strip())

genre_list = ["All"] + sorted(list(all_genres))

selected_genre = st.sidebar.selectbox("Select Genre", genre_list)
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 7.0, 0.1)
min_votes = st.sidebar.slider("Minimum Votes", 0, 20000, 500, 100)


# ---- Helper Function to Query Movies ----
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


# ---- Query and Display Movies ----
st.subheader("🎥 Filtered Movies")
movies_df = get_filtered_movies(selected_genre, min_rating, min_votes)

if not movies_df.empty:
    st.dataframe(movies_df, use_container_width=True)
else:
    st.warning("No movies match your filters. Try lowering the thresholds.")

