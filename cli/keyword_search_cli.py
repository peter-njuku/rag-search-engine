#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description="Key word Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parsers = subparsers.add_parser("search", help="Search movies using BM25")
    search_parsers.add_argument("query", type=str, help="Search query")
    
    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            #pass
            movie_path = Path(__file__).parent.parent / "data" / "movies.json"

            with open(movie_path, "r") as f:
                data = json.load(f)
                movies = data.get("movies", data)
            results = []
            for movie in movies:
                if args.query.lower() in movie["title"].lower():
                    results.append(movie)

            for i, movie in enumerate(results[:5], start=1):
                print(f"{i}. {movie["title"]} {i}")
                    
                    
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()