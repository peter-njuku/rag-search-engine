def load_stopwords():
    with open("data/stopwords.txt", "r") as f:
        stopwords = set(f.read().splitlines())
    return stopwords
        