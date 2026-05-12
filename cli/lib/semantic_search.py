from sentence_transformers import SentenceTransformer


class SemanticSearch:
    def __init__(self, ):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embedding(self, text):
        if not isinstance(text, str):
            raise ValueError("[Error] - Input text must be a string.")
        if not text.strip():
            raise ValueError("[Error] - Input text cannot be empty or only whitespace.")

        embedding_list = self.model.encode([text])
        return embedding_list[0]


def verify_model():
    semantic_search = SemanticSearch()
    print(f"Model loaded successfully: {semantic_search.model}")
    print("Max sequence length:", semantic_search.model.max_seq_length)

def embed_text(text):
    semantic_search = SemanticSearch()
    embedding = semantic_search.generate_embedding(text)   
    print(f"Text: {text}")
    print(f"First 3 dimensions: {embedding[:3]}")
    print(f"Dimensions: {embedding.shape[0]}")

if __name__ == "__main__":
    verify_model()