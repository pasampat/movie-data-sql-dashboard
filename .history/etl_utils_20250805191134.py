"""
etl_utils.py

ETL (Extract, Transform, Load) utilities for TMDB/IMDb movie datasets:
- Load CSV → pandas DataFrame
- Clean DataFrame (flatten JSON-like fields, drop NAs, extract release_year)
- Save DataFrame → SQLite database
- Archive processed CSVs

Designed for simple, SQL-friendly tables.
"""

import pandas as pd
import sqlite3
from pathlib import Path
import shutil
import ast  # For safely evaluating stringified JSON lists


def load_csv_to_dataframe(csv_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the CSV data.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(path)
    return df


def extract_genres(genre_str: str) -> str:
    """
    Convert a JSON-like genres string into a pipe-separated string.

    Example:
    '[{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}]'
    -> "Action|Adventure"

    Returns None if parsing fails.
    """
    try:
        genres_list = ast.literal_eval(genre_str)
        return "|".join(g["name"] for g in genres_list if "name" in g)
    except:
        return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and flatten the TMDB movie dataset for SQL usage.

    Steps:
    - Drop rows missing 'title'
    - Extract release_year from release_date
    - Flatten genres into pipe-separated string
    - Keep only SQL-friendly columns

    Parameters
    ----------
    df : pd.DataFrame
        Original DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned and flattened DataFrame.
    """
    # Drop rows with missing essential title
    if "title" in df.columns:
        df = df.dropna(subset=["title"])

    # Extract release_year from release_date (if present)
    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df["release_year"] = df["release_date"].dt.year
    else:
        df["release_year"] = None

    # Flatten genres column if present
    if "genres" in df.columns:
        df["genres"] = df["genres"].apply(extract_genres)
    else:
        df["genres"] = None

    # Keep only useful columns for SQL queries
    keep_cols = [
        "id", "title", "release_year", "vote_average", "vote_count",
        "popularity", "budget", "revenue", "genres"
    ]
    df = df[[col for col in keep_cols if col in df.columns]]

    # Drop rows missing release_year or title after processing
    df = df.dropna(subset=["title", "release_year"])

    # Strip whitespace in string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    return df


def save_dataframe_to_sqlite(
    df: pd.DataFrame, db_path: str = "data.db", table_name: str = "movies"
) -> None:
    """
    Save a DataFrame to an SQLite database (replaces table if exists).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    db_path : str
        Path to the SQLite database file.
    table_name : str
        Name of the table to create/replace.

    Returns
    -------
    None
    """
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()


def archive_file(csv_path: str, archive_dir: str = "archive") -> None:
    """
    Move a processed CSV file into an archive directory.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file to archive.
    archive_dir : str
        Directory where the file should be archived.

    Returns
    -------
    None
    """
    path = Path(csv_path)
    archive_folder = Path(archive_dir)
    archive_folder.mkdir(exist_ok=True)

    shutil.move(str(path), archive_folder / path.name)


def load_csv_to_sqlite(
    csv_path: str, db_path: str = "data.db", table_name: str = "movies", archive: bool = True
) -> None:
    """
    Full ETL pipeline:
    1. Load CSV → DataFrame
    2. Clean DataFrame (flatten JSON-like fields)
    3. Save DataFrame → SQLite
    4. Archive original CSV (optional)

    Parameters
    ----------
    csv_path : str
        Path to the CSV file to process.
    db_path : str
        Path to the SQLite database file.
    table_name : str
        Name of the table to create/replace.
    archive : bool
        Whether to move the CSV to /archive after processing.

    Returns
    -------
    None
    """
    df = load_csv_to_dataframe(csv_path)
    df = clean_dataframe(df)
    save_dataframe_to_sqlite(df, db_path, table_name)

    if archive:
        archive_file(csv_path)

    print(
        f"✅ Loaded {len(df)} rows into '{db_path}' (table: '{table_name}')."
        + (f"\n📦 Archived file: {csv_path} → archive/{Path(csv_path).name}" if archive else "")
    )
