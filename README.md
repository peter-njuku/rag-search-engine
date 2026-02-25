# RAG Search Engine

A keyword-based search engine for movies using inverted index technology.

---

## For End Users

### What is this app?

This is a movie search application that helps you find movies quickly and easily by searching for keywords. Simply type what you're looking for, and the app will return matching movies from its database.

### How to use it

1. **Build the search index** (one-time setup):
   ```bash
   python -m cli.keyword_search_cli build
   ```

2. **Search for movies**:
   ```bash
   python -m cli.keyword_search_cli search "your search query"
   ```

   Example: `python -m cli.keyword_search_cli search "action adventure"`

### Features

- Fast keyword search across movie titles and descriptions
- Automatic handling of common words (stopword filtering)
- Word form normalization (so "running" matches "runs")
- Case-insensitive searching
- Returns matching movie titles

---

## For Developers

### Architecture

The application uses an **inverted index** data structure for efficient keyword searching:

- **InvertedIndex class**: Maintains a mapping of tokens (words) to the movies they appear in
- **Preprocessing**: Text is tokenized, lowercased, cleaned of punctuation, stopwords are removed, and words are stemmed
- **Caching**: Built indices are serialized and cached in the `cache/` directory for fast reloading

### Project Structure

```
├── cli/
│   ├── keyword_search_cli.py    # CLI interface and inverted index implementation
│   ├── stopwords.py              # Stopword loading utilities
│   └── __pycache__/
├── data/
│   ├── movies.json              # Movie database
│   └── stopwords.txt            # List of common stopwords
├── cache/                        # Cached index files
├── main.py                       # Entry point
├── pyproject.toml                # Project configuration
└── README.md
```

### Key Components

**InvertedIndex class** (`cli/keyword_search_cli.py`):
- `build()`: Reads movies.json and constructs inverted index
- `save()`: Persists index to disk (cache/)
- `get_documents(term)`: Returns movie IDs matching a term
- `__add_document()`: Internal method to process and index a document

**Text Processing Pipeline**:
1. Lowercase text
2. Remove punctuation
3. Tokenize into words
4. Remove stopwords (common words like "the", "and", "a")
5. Apply Porter Stemmer (normalize words, e.g., "running" → "run")

### Setup for Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # or
   pip install nltk==3.9.1
   ```

2. **Build the index**:
   ```bash
   python -m cli.keyword_search_cli build
   ```

### Adding More Features

- **BM25 ranking**: Currently the search supports basic keyword matching. Consider implementing BM25 ranking for relevance scoring
- **Phrase search**: Support searching for exact phrases
- **Filters**: Add ability to filter by genre, release year, rating, etc.
- **Pagination**: Handle large result sets

### Data Format

Movies are stored in `data/movies.json` in the following format:
```json
{
  "movies": [
    {
      "title": "Movie Title",
      "description": "Movie description text"
    }
  ]
}
```

### Dependencies

- **nltk** (3.9.1): Natural Language Toolkit for stemming and text processing
- **Python** (3.12+): Required Python version

---

*Last updated: February 25, 2026*
