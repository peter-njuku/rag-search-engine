def load_stopwords() -> set:
    with open("data/stopwords.txt", "r") as f:
        stopwords = set(f.read().splitlines())
    return stopwords
        