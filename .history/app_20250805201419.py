# ---- PAGE HEADER ----
st.title("🎬 Movie Data SQL Dashboard")
st.markdown("**Explore movies by rating, popularity, and genre using a SQLite backend.**")

# Show total movies in dataset as a clear headline metric
total_movies_df = run_query("SELECT COUNT(*) as total FROM movies")
total_movies = total_movies_df["total"].iloc[0]
st.markdown(f"### 📊 Dataset contains **{total_movies:,} movies**")

# ---- KPI CARDS ----
st.subheader("🎯 Key Insights")
if not movies_df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("🎬 Movies Matching Filters", len(movies_df))
    col2.metric("⭐ Average Rating", round(movies_df["vote_average"].mean(), 2))
    top_genre = movies_df["genres"].mode()[0] if not movies_df.empty else "N/A"
    col3.metric("🎭 Most Common Genre", top_genre)
else:
    st.info("No movies match your filters. Adjust the sidebar to see results.")


# ---- FILTERED MOVIES TABLE ----
st.subheader("🎥 Filtered Movies — Top 50 by Rating")
st.markdown("**Shows movies that meet your selected filters: genre, minimum rating, and minimum votes.**")

if not movies_df.empty:
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


# ---- AVERAGE RATING PER YEAR CHART ----
st.subheader("📈 Average Rating Per Year")
st.markdown("**Shows how the average rating of movies matching your filters changes over time.**")

if not rating_df.empty:
    st.line_chart(rating_df.set_index("release_year"))
else:
    st.info("Not enough data for the selected filters to plot ratings by year.")


# ---- GENRE DISTRIBUTION PIE CHART ----
st.subheader("🥧 Top 10 Genre Combinations by Movie Count")
st.markdown("**Shows the top 10 most common genre combinations in the dataset.**")

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
