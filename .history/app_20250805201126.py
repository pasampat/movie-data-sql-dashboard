"""
app.py

Polished Movie SQL Dashboard
- Friendly labels and simplified layout for clarity
- KPI cards for instant context
- Progressive flow: KPIs → Table → Trend → Genre Pie
"""

import streamlit as st
import pandas as pd
from sql_utils import run_query
import plotly.express as px

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

all_genres = set()
for g in genre_df["genres"]:
    for item in g.split("|"):
        all_genres.add(item.strip())

genre_list = ["All"] + sorted(list(all_genres))
selected_genre = st.sidebar.selectbox("Select Genre", genre_list)

min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 7.0, 0.1)
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


# ---- Fetch Filtered Movies ----
movies_df = get_filtered_movies(selected_genre, min_rating, min_votes)

# ---- KPI Cards ----
st.subheader("🎯 Key Insights")
if not movies_df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("🎬 Movies Matching Filters", len(movies_df))
    col2.metric("⭐ Average Rating", round(movies_df["vote_average"].mean(), 2))
    top_genre = movies_df["genres"].mode()[0] if not movies_df.empty else "N/A"
    col3.metric("🎭 Most Common Genre", top_genre)
else:
    st.info("No movies match your filters. Adjust the sidebar to see results.")


# ---- Filtered Movies Table ----
st.subheader("🎥 Filtered Movies — Top 50 by Rating")
st.caption("Shows movies that meet your selected filters: genre, minimum rating, and minimum votes.")

if not movies_df.empty:
    # Rename for display clarity
    display_df = movies_df.rename(columns={
        "title": "Title",
        "release_year": "Year",
        "vote_average": "Average Rating",
        "vote_count": "Votes",
        "genres": "Genres"
    })[["Title", "Year", "Average Rating", "Votes", "Genres"]]

    st.dataframe(display_df, use_container_width=True)
else:
    st.warning("No movies available to display in the table.")


# ---- Average Rating Per Year ----
st.subheader("📈 Average Rating Per Year")
st.caption("See how the average rating of movies matching your filters changes over time.")

rating_trend_query = f"""
SELECT release_year, ROUND(AVG(vote_average), 2) AS avg_rating
FROM movies
WHERE vote_average >= {min_rating} AND vote_count >= {min_votes}
{"" if selected_genre == "All" else f"AND genres LIKE '%{selected_genre}%' "}
GROUP BY release_year
ORDER BY release_year;
"""
rating_df = run_query(rating_trend_query)

if not rating_df.empty:
    st.line_chart(rating_df.set_index("release_year"))
else:
    st.info("Not enough data for the selected filters to plot ratings by year.")


# ---- Genre Distribution Pie Chart ----
st.subheader("🥧 Top 10 Genre Combinations by Movie Count")
st.caption("Shows the most common genre combinations among the filtered movies.")

genre_count_query = f"""
SELECT genres, COUNT(*) AS movie_count
FROM movies
WHERE genres IS NOT NULL
  AND vote_average >= {min_rating} 
  AND vote_count >= {min_votes}
  {"" if selected_genre == "All" else f"AND genres LIKE '%{selected_genre}%' "}
GROUP BY genres
ORDER BY movie_count DESC
LIMIT 10;
"""
genre_count_df = run_query(genre_count_query)

if not genre_count_df.empty:
    fig = px.pie(
        genre_count_df,
        values="movie_count",
        names="genres",
        title="Top 10 Genre Combinations",
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No genre data available for the selected filters.")
