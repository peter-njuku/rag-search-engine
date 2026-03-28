from sentence_transformers import SentenceTransformer


class SemanticSearch:
    def __init__(self, ):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')


def verify_model():
    semantic_search = SemanticSearch()
    print(f"Model loaded successfully: {semantic_search.model}")
    print("Max sequence length:", semantic_search.model.max_seq_length)

if __name__ == "__main__":
    verify_model()