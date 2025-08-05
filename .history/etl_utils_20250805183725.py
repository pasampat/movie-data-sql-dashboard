"""
etl_utils.py

Clean, modular ETL (Extract, Transform, Load) utilities:
- Load CSV → pandas DataFrame
- Clean DataFrame (drop NAs, simple cleanup)
- Save DataFrame → SQLite database
- Archive processed CSVs

Designed to be simple, readable, and maintainable.
"""

import pandas as pd
import sqlite3
from pathlib import Path
import shutil


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

    # Read CSV (UTF-8 by default for safety)
    df = pd.read_csv(path)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform simple, predictable cleaning steps on the DataFrame.

    - Drop rows where the 'title' column is missing.
    - Strip leading/trailing whitespace from string columns.

    Parameters
    ----------
    df : pd.DataFrame
        Original DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    # Drop rows with missing essential fields (example: 'title')
    if "title" in df.columns:
        df = df.dropna(subset=["title"])

    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    return df


def save_dataframe_to_sqlite(
    df: pd.DataFrame, db_path: str = "data.db", table_name: str = "movies"
) -> None:
    """
    Save a DataFrame to an SQLite database.

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

    # Move file to archive
    shutil.move(str(path), archive_folder / path.name)


def load_csv_to_sqlite(
    csv_path: str, db_path: str = "data.db", table_name: str = "movies"
) -> None:
    """
    Full ETL pipeline:
    1. Load CSV → DataFrame
    2. Clean DataFrame
    3. Save DataFrame → SQLite
    4. Archive original CSV

    Parameters
    ----------
    csv_path : str
        Path to the CSV file to process.
    db_path : str
        Path to the SQLite database file.
    table_name : str
        Name of the table to create/replace in the database.

    Returns
    -------
    None
    """
    df = load_csv_to_dataframe(csv_path)
    df = clean_dataframe(df)
    save_dataframe_to_sqlite(df, db_path, table_name)
    archive_file(csv_path)

    print(
        f"✅ Loaded {len(df)} row
