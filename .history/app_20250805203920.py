"""
app.py

Final Polished Movie SQL Dashboard
- Smaller, simpler layout
- Clear narrative flow: Dataset → Table → KPIs → Line Chart → Pie Chart
- Percentages on pie slices, legend shows genres
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sql_utils import run_query

st.set_page_config(page_title="🎬 Movie SQL Dashboard", layout="wide")

# ------------------ PAGE HEADER ------------------
st.subheader("🎬 Movie Data SQL Dashboard")
st.markdown("Explore movies by rating, popularity, and genre using a SQLite backend.")

# Show total movies in dataset
total_movies_df = run_query("SELECT COUNT(*) as total FROM movies")
total_movies = total_movies_df["total"].iloc[0]
st.markdown(f"#### 📊 Dataset contains **{total_movies:,} movies**")

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("Filters")

# Get all unique genres
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
min_votes = st.sidebar.slider("Minimum Votes", 0, 13000, 500, 100)

# ------------------ FILTERED MOVIES FUNCTION ------------------
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

# Fetch filtered movies
movies_df = get_filtered_movies(selected_genre, min_rating, min_votes)

# ------------------ FILTERED MOVIES TABLE ------------------
st.markdown("#### 🎥 Filtered Movies")
st.markdown(
    "Use the filters on the left to choose a genre, minimum rating, and minimum votes. "
    "The table below shows up to 50 movies that meet your selected criteria, sorted by rating."
)

if not movies_df.empty:
    display_df = movies_df.rename(columns={
        "title": "Title",
        "release_year": "Year",
        "vote_average": "Average Rating",
        "vote_count": "Votes",
        "genres": "Genres"
    })[["Title", "Year", "Average Rating", "Votes", "Genres"]]

    # Display table with index starting at 1
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True)
else:
    st.warning("No movies available to display with the current filters.")

# ------------------ KPI CARDS ------------------
st.markdown("#### 🎯 Key Insights")
st.markdown("Summary of the movies currently visible in the table above:")

if not movies_df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("🎬 Movies Displayed", len(movies_df))
    col2.metric("⭐ Average Rating", round(movies_df["vote_average"].mean(), 2))
    top_genre = movies_df["genres"].mode()[0] if not movies_df.empty else "N/A"
    col3.metric("🎭 Most Common Genre", top_genre)
else:
    st.info("No movies match your filters to calculate insights.")

# ------------------ AVERAGE RATING PER YEAR ------------------
st.markdown("#### 📈 Average Rating Per Year")
st.markdown("Shows how the average rating of movies that meet your filters changes over time.")

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

# ------------------ GENRE DISTRIBUTION PIE CHART ------------------
st.subheader("🥧 Top 10 Genre Combinations by Movie Count")
st.markdown("Shows the most common genre combinations among the filtered movies.")

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
        hole=0.3
    )
    # Show only percentages on slices
    fig.update_traces(textposition='inside', textinfo='percent')
    # Make pie chart smaller
    fig.update_layout(height=350, width=500)
    st.plotly_chart(fig, use_container_width=False)
else:
    st.info("No genre data available for the selected filters.")
