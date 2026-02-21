#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import string

from stopwords import load_stopwords

stopwords = load_stopwords()

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
            translator = str.maketrans("", "", string.punctuation)

            clean_query = args.query.lower().translate(translator)
            query_tokens = [t for t in clean_query.split() if t not in stopwords]
        
            query_token_set = set(query_tokens)

            for movie in movies:

                
                
                clean_title = movie["title"].lower().translate(translator)
                title_tokens = [t for t in clean_title.split() if t not in stopwords]
                title_token_set = set(title_tokens)

                if any(q in t for q in query_token_set for t in title_token_set):
                    results.append(movie)

            for i, movie in enumerate(results[:5], start=1):
                print(f"{i}. {movie['title']} {i}")
                    
                    
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()