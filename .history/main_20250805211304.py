from etl_utils import load_csv_to_sqlite
from sql_utils import top_10_movies, high_rated_popular_movies, movies_per_genre, top_movies_by_genre

from tabulate import tabulate


def main():
    # 1. Run ETL 
    print("\n=== Running ETL ===")
    load_csv_to_sqlite("data/movies.csv")

    # 2. Print Top 10 Movies by Rating
    print("\n=== Top 10 Movies by Rating ===")
    df_top10 = top_10_movies()
    print(tabulate(df_top10, headers="keys", tablefmt="pretty"))

    # 3. Print High-Rated & Popular Movies
    print("\n=== High-Rated & Popular Movies (Rating >= 8, Votes >= 1000) ===")
    df_high_rated = high_rated_popular_movies(min_rating=8.0, min_votes=1000)
    print(tabulate(df_high_rated, headers="keys", tablefmt="pretty"))


    print("\n=== Movies Per Genre ===")
    print(tabulate(movies_per_genre(), headers="keys", tablefmt="pretty"))

    print("\n=== Top Action Movies by Rating ===")
    print(tabulate(top_movies_by_genre("Action"), headers="keys", tablefmt="pretty"))



if __name__ == "__main__":
    main()
