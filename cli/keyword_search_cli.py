#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import pickle
import string

from stopwords import load_stopwords
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

stopwords = load_stopwords()

def cache_dir() -> Path:
    os.makedirs("cache", exist_ok=True)
    return Path("cache")

class InvertedIndex:
    def __init__(self, index: dict[str, set[int]], docmap: dict[int, str]):
        self.index = index
        self.docmap = docmap
        self.index_doc = cache_dir() / "index.pkl"
        self.docmap_doc = cache_dir() / "docmap.pkl"

    def __add_document(self, doc_id, text):
        translator = str.maketrans("", "", string.punctuation)
        clean_text = text.lower().translate(translator)
        tokens = [t for t in clean_text.split() if t not in stopwords]
        stem = lambda t: stemmer.stem(t)
        tokens = [stem(t) for t in tokens]

        for token in tokens:
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(doc_id)

    def get_documents(self, term):
        return sorted(list(self.index.get(term.lower(), set())))
    def build(self):
        movie_path = Path(__file__).parent.parent / "data" / "movies.json"

        with open(movie_path, "r") as f:
            data = json.load(f)
            movies = data.get("movies", data)


        for i, movie in enumerate(movies, start=1):
            text = f"{movie['title']} {movie['description']}"
            self.__add_document(i, text)
            self.docmap[i] = movie["title"]

            


    def save(self):
        with open (self.index_doc, "wb") as f:
            pickle.dump(self.index, f)

        with open (self.docmap_doc, "wb") as f:
            pickle.dump(self.docmap, f)

def main() -> None:
    parser = argparse.ArgumentParser(description="Key word Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parsers = subparsers.add_parser("search", help="Search movies using BM25")
    build_parser = subparsers.add_parser("build", help="Build Inverted Index")

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
            stem = lambda t: stemmer.stem(t)
            query_tokens = [stem(t) for t in query_tokens]
            print(query_tokens)
            query_token_set = set(query_tokens)

            for movie in movies:                
                clean_title = movie["title"].lower().translate(translator)
                title_tokens = [t for t in clean_title.split() if t not in stopwords]
                title_token_set = set(title_tokens)

                if any(q in t for q in query_token_set for t in title_token_set):
                    results.append(movie)

            for i, movie in enumerate(results[:5], start=1):
                print(f"{i}. {movie['title']} {i}")

        case "build":
            print("Building Inverted index")
            index = InvertedIndex({}, {})
            index.build()
            index.save()
            docs = index.get_documents("merida") if "merida" else None
            print(f"First document for token 'merida' = {docs[0]}") if docs else None

                    
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()