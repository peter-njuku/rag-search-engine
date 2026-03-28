#!/usr/bin/env python3

import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import pickle
import string

from stopwords import load_stopwords
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()
stopwords = load_stopwords()
BM25_K1 = 1.5
BM25_B = 0.75

def cache_dir() -> Path:
    os.makedirs("cache", exist_ok=True)
    return Path("cache")

class InvertedIndex:
    def __init__(self, index: dict[str, set[int]], docmap: dict[int, str], term_freq: dict[str, Counter] = None):
        self.index = index
        self.docmap = docmap
        self.term_freq = term_freq or {}
        self.index_doc = cache_dir() / "index.pkl"
        self.docmap_doc = cache_dir() / "docmap.pkl"
        self.term_freq_doc = cache_dir() / "term_freq.pkl"
        self.doc_lengths = {}
        self.doc_lengths_doc = cache_dir() / "doc_lengths.pkl"


    def __add_document(self, doc_id, text):
        translator = str.maketrans("", "", string.punctuation)
        clean_text = text.lower().translate(translator)
        tokens = [t for t in clean_text.split() if t not in stopwords]
        stem = lambda t: stemmer.stem(t)
        tokens = [stem(t) for t in tokens]
        token_counter = Counter(tokens)

        self.doc_lengths[doc_id] = len(tokens)

        self.term_freq[doc_id] = token_counter


        for token in tokens:
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(doc_id)

    def __get_avg_doc_length(self) -> float:
        total_length = sum(self.doc_lengths.values())
        num_docs = len(self.doc_lengths)
        return total_length / num_docs if num_docs > 0 else 0.0

    def get_documents(self, term):
        """
        Get Documents with indexes in a sorted manner
        """
        return sorted(list(self.index.get(term.lower(), set())))
    

    def build(self):
        """
        Building Inverted Index 
        """
        movie_path = Path(__file__).parent.parent / "data" / "movies.json"

        with open(movie_path, "r") as f:
            data = json.load(f)
            movies = data.get("movies", data)


        for i, movie in enumerate(movies, start=1):
            text = f"{movie['title']} {movie['description']}"
            self.__add_document(i, text)
            self.docmap[i] = movie["title"]

    def get_tf(self, doc_id, term) -> int:
        """
        Get term frequency for a given document and term
        """
        translator = str.maketrans("", "", string.punctuation)
        clean_term = term.lower().translate(translator)
        tokens = clean_term.split()
        if len(tokens) > 1:
            raise ValueError(f"Term should be a single token, get mutiple tokens instead: {tokens}")
        
        stem = lambda t: stemmer.stem(t)
        tokens = [stem(t) for t in tokens]

        tf = self.term_freq.get(doc_id, {}).get(tokens[0], 0)
        return tf

    def get_total_documents(self):
        return len(self.docmap)

    def get_idf(self, term):
        translator = str.maketrans("", "", string.punctuation)
        clean_term = term.lower().translate(translator)
        tokens = clean_term.split()
        if len(tokens) > 1:
            raise ValueError(f"Term should be a single token, get mutiple tokens instead: {tokens}")    
        stem = lambda t: stemmer.stem(t)
        tokens = [stem(t) for t in tokens]
        doc_count = self.get_total_documents()
        doc_freq = len(self.index.get(tokens[0], set()))

        idf = math.log((doc_count + 1) / (doc_freq + 1))
        return idf
    
    def get_tfidf(self, doc_id, term) -> float:
        """
        Get TF-IDF score for a given document and term
        """
        tf = self.get_tf(doc_id, term)
        idf = self.get_idf(term)
        tfidf = tf * idf
        return tfidf

    def get_bm25_idf(self, term: str) -> float:
        translator = str.maketrans("", "", string.punctuation)
        clean_term = term.lower().translate(translator)
        tokens = clean_term.split()
        if len(tokens) > 1:
            raise ValueError(f"Term should be a single token, get mutiple tokens instead: {tokens}")
        stem = lambda t: stemmer.stem(t)
        tokens = [stem(t) for t in tokens]
        doc_count = self.get_total_documents()
        doc_freq = len(self.index.get(tokens[0], set()))
        bm25_idf_score = math.log((doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1)

        return bm25_idf_score

    def get_bm25_tf(self, doc_id:int, term: str, k1=BM25_K1, b:float=BM25_B) -> float:
        tf = self.get_tf(doc_id, term)

        doc_length = self.doc_lengths.get(doc_id, 0)
        avg_doc_length = self.__get_avg_doc_length()

        if avg_doc_length > 0:
            length_norm = (1 - b) + b * (doc_length / avg_doc_length)
        else:
            length_norm = 1.0
            
        saturated_tf_score = (tf * (k1 + 1)) / (tf + k1 * length_norm) #if tf > 0 else 0.0
        return saturated_tf_score

    def bm25_tf_command(doc_id: int, term:str, k1:float | None, b:float=BM25_B) -> float:
        index = InvertedIndex({}, {})
        index.load()
        bm25_tf_score = index.get_bm25_tf(doc_id, term, k1, b)
        return bm25_tf_score


    def save(self):
        with open (self.index_doc, "wb") as f:
            pickle.dump(self.index, f)

        with open (self.docmap_doc, "wb") as f:
            pickle.dump(self.docmap, f)

        with open (self.term_freq_doc, "wb") as f:
            pickle.dump(self.term_freq, f)

        with open(self.doc_lengths_doc, "wb") as f:
            pickle.dump(self.doc_lengths, f)

    def load(self):
        try:
            with open (self.index_doc, "rb") as f:
                self.index = pickle.load(f)

            with open (self.docmap_doc, "rb") as f:
                self.docmap = pickle.load(f)

            with open (cache_dir() / "term_freq.pkl", "rb") as f:
                self.term_freq = pickle.load(f)

            with open(cache_dir() / "doc_lengths.pkl", "rb") as f:
                self.doc_lengths = pickle.load(f)

        except FileNotFoundError:
            print("No cached index found. Please run 'build' command first.")
            exit(1)

def bm25_idf_command(term: str) -> float:
    """
    Get the BM25 IDF score for a given term.
    
    Args:
        term: The term to calculate BM25 IDF for
        
    Returns:
        The BM25 IDF score as a float
    """
    index = InvertedIndex({}, {})
    index.load()
    bm25_idf_score = index.get_bm25_idf(term)
    return bm25_idf_score

def main() -> None:
    parser = argparse.ArgumentParser(description="Key word Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parsers = subparsers.add_parser("search", help="Search movies using BM25")
    search_parsers.add_argument("query", type=str, help="Search query")

    build_parser = subparsers.add_parser("build", help="Build Inverted Index")

    tf_parser = subparsers.add_parser("tf", help="Get term frequency for a given document and term")
    tf_parser.add_argument("doc_id", type=int, help="Document ID")
    tf_parser.add_argument("term", type=str, help="Term to get frequency for")

    idf_parser = subparsers.add_parser("idf", help="Get inverse document frequency for a given term")
    idf_parser.add_argument("term", type=str, help="Term to get IDF for")
    
    tfidf_parser = subparsers.add_parser("tfidf", help="Get TF-IDF score for a given document and term")
    tfidf_parser.add_argument("doc_id", type=int, help="Document ID")
    tfidf_parser.add_argument("term", type=str, help="Term to get TF-IDF score for")

    bm25_idf_parser = subparsers.add_parser("bm25idf", help="Get BM25 IDF score for a given term")
    bm25_idf_parser.add_argument("term", type=str, help="Term to get BM25 IDF score for")

    bm25_tf_parser = subparsers.add_parser( "bm25tf", help="Get BM25 TF score for a given document ID and term")
    bm25_tf_parser.add_argument("doc_id", type=int, help="Document ID")
    bm25_tf_parser.add_argument("term", type=str, help="Term to get BM25 TF score for")
    bm25_tf_parser.add_argument("k1", type=float, nargs='?', default=BM25_K1, help="Tunable BM25 K1 parameter")
    bm25_tf_parser.add_argument("b", type=float, nargs='?', default=BM25_B, help="Tunable BM25 B parameter")

    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            #pass
            index = InvertedIndex({}, {})
            index.load()

            # with open(movie_path, "r") as f:
            #     data = json.load(f)
            #     movies = data.get("movies", data)
            results = []
            translator = str.maketrans("", "", string.punctuation)

            clean_query = args.query.lower().translate(translator)
            query_tokens = [t for t in clean_query.split() if t not in stopwords]
            stem = lambda t: stemmer.stem(t)
            query_tokens = [stem(t) for t in query_tokens]
            # print(query_tokens)
            query_token_set = set(query_tokens)

            for token in query_token_set:
                doc_ids = index.get_documents(token)
                results.extend(doc_ids)

            unique_results = list(set(results))

            # for movie in movies:                
            #     clean_title = movie["title"].lower().translate(translator)
            #     title_tokens = [t for t in clean_title.split() if t not in stopwords]
            #     title_token_set = set(title_tokens)

            #     if any(q in t for q in query_token_set for t in title_token_set):
            #         results.append(movie)

            for i, doc_id in enumerate(unique_results, start=1):
                print(f"{i}. {index.docmap[doc_id]} ")

        case "build":
            print("Building Inverted index")
            index = InvertedIndex({}, {})
            index.build()
            index.save()
            # docs = index.get_documents("merida") if "merida" else None
            # print(f"First document for token 'merida' = {docs[0]}") if docs else None


        case "tf":           
            print(f"Getting term frequency for doc_id: {args.doc_id}, term: {args.term}")
            index = InvertedIndex({}, {})
            index.load()
            tf = index.get_tf(args.doc_id, args.term)
            try:
                tf = index.get_tf(args.doc_id, args.term)
                print(tf)
            except ValueError as e:
                print(f"Error: {e}")
                exit(1)

        case "idf":
            print(f"Getting inverse document frequency for term: {args.term}")
            index = InvertedIndex({}, {})
            index.load()
            try:
                idf = index.get_idf(args.term)
                print(f"Inverse document frequency of '{args.term}': {idf:.2f}")
            except ValueError as e:
                print(f"Error: {e}")
                exit(1)

        case "tfidf":
            print(f"Getting TF-IDF score for doc_id: {args.doc_id}, term: {args.term}")
            index = InvertedIndex({}, {})
            index.load()
            try:
                tf_idf = index.get_tfidf(args.doc_id, args.term)
                print(f"TF-IDF score of '{args.term}' in document '{args.doc_id}': {tf_idf:.2f}")
            except ValueError as e:
                print(f"Error: {e}")
                exit(1)


        case "bm25idf":
            print(f"Getting BM25 IDF score for term: {args.term}")
            try:      
                bm25_idf_score = bm25_idf_command(args.term)
                print(f"BM25 IDF score of '{args.term}': {bm25_idf_score:.2f}")
            except ValueError as e:
                print(f"Error: {e}")
                exit(1)
        case "bm25tf":
            print(f"Getting BM25 TF score for doc_id: {args.doc_id}, term: {args.term}, k1: {args.k1}, b: {args.b}")
            try:
                bm25_tf_score = InvertedIndex.bm25_tf_command(args.doc_id, args.term, args.k1, args.b)
                print(f"BM25 TF score of '{args.term}' in document '{args.doc_id}': {bm25_tf_score:.2f}")
            except ValueError as e:
                print(f"Error: {e}")
                exit(1) 

        case _:
            parser.print_help()

if __name__ == "__main__":
    main()