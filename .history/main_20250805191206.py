from etl_utils import load_csv_to_sqlite

load_csv_to_sqlite("data/movies.csv", archive=False)
