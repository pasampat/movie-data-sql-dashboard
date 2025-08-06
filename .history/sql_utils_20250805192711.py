"""
sql_utils.py

SQL query utilities for the movie database.
- Connects to SQLite
- Provides functions for common analysis queries
- Returns results as pandas DataFrames for CLI or Streamlit
"""

import sqlite3
import pandas as pd
from tabulate import tabulate

DB_PATH = "data.db"


def run_query(query: str) -> pd.DataFrame:
    """
    Run a SQL query on the SQLite database and return a DataFrame.

    Parameters
    ----------
    query : str
        SQL query to execute.

    Returns
    -------
    pd.DataFrame
        Query results as a DataFrame.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def top_10_movies(limit: int = 10) -> pd.DataFrame:
    """
    Return top movies by rating.

    Parameters
    ----------
    limit : int
        Number of top movies to return. Default 10.

    Returns
    -------
    pd.DataFrame
        DataFrame of top movies sorted by vote_average.
    """
    query = f"""
    SELECT title, vote_average
    FROM movies
    ORDER BY vote_average DESC
    LIMIT {limit};
    """
    return run_query(query)


def high_rated_popular_movies(min_rating: float = 8.0, min_votes: int = 1000) -> pd.DataFrame:
    """
    Return movies with rating >= min_rating and vote_count >= min_votes.

    Parameters
    ----------
    min_rating : float
        Minimum vote_average to filter.
    min_votes : int
        Minimum vote_count to filter.

    Returns
    -------
    pd.DataFrame
        Filtered movies sorted by vote_average descending.
    """
    query = f"""
    SELECT title, release_year, vote_average, vote_count
    FROM movies
    WHERE vote_average >= {min_rating} AND vote_count >= {min_votes}
    ORDER BY vote_average DESC
    LIMIT 10;
    """
    return run_query(query)


def movies_per_genre(limit: int = 20) -> pd.DataFrame:
    """
    Count movies grouped by their genre string.
    Shows the most common genre combinations.
    """
    query = f"""
    SELECT genres, COUNT(*) as movie_count
    FROM movies
    WHERE genres IS NOT NULL
    GROUP BY genres
    ORDER BY movie_count DESC
    LIMIT {limit};
    """
    return run_query(query)


def top_movies_by_genre(genre: str, limit: int = 10) -> pd.DataFrame:
    """
    Return top movies by rating within a specific genre.
    """
    query = f"""
    SELECT title, vote_average, vote_count, genres
    FROM movies
    WHERE genres LIKE '%{genre}%'
    ORDER BY vote_average DESC
    LIMIT {limit};
    """
    return run_query(query)



if __name__ == "__main__":
    # CLI Test
    print("=== Top 10 Movies by Rating ===")
    print(tabulate(top_10_movies(), headers="keys", tablefmt="pretty"))

    print("\n=== High Rated & Popular Movies (Rating >= 8, Votes >= 1000) ===")
    print(tabulate(high_rated_popular_movies(), headers="keys", tablefmt="pretty"))
