"""
QnA Bot - Embedding and FAISS Indexing Script
This script creates embeddings for the QnA dataset and stores them using FAISS.
Uses TF-IDF vectorization as an alternative to sentence-transformers.
"""

import pandas as pd
import numpy as np
import re
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

# Step 1: Load and preprocess the dataset
def load_and_preprocess_data(csv_file):
    """Load CSV and preprocess the text data."""
    df = pd.read_csv(csv_file)
    
    # Remove any null or empty entries
    df = df.dropna()
    df = df[df['Question'].str.strip() != '']
    df = df[df['Answer'].str.strip() != '']
    
    print(f"Loaded {len(df)} Q&A pairs")
    return df

def clean_text(text):
    """Clean text by removing symbols and converting to lowercase."""
    if isinstance(text, str):
        # Remove special characters but keep spaces
        text = re.sub(r'[^A-Za-z\s]', '', text)
        text = text.lower().strip()
    else:
        text = ''
    return text

# Step 2: Create embeddings using TF-IDF
def create_embeddings(questions):
    """Create embeddings for questions using TF-IDF."""
    print("Creating TF-IDF embeddings...")
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),  # Use unigrams and bigrams
        max_features=500,
        stop_words='english'
    )
    
    # Fit and transform questions
    embeddings = vectorizer.fit_transform(questions).toarray()
    
    print(f"Embeddings shape: {embeddings.shape}")
    return vectorizer, embeddings

# Step 3: Create FAISS index and save
def create_faiss_index(embeddings, index_file='qa_faiss.index'):
    """Create FAISS index and save to disk."""
    d = embeddings.shape[1]  # Dimension of embeddings
    
    # Using IndexFlatL2 for Euclidean distance
    index = faiss.IndexFlatL2(d)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    # Save the index
    faiss.write_index(index, index_file)
    print(f"FAISS index saved to {index_file}")
    
    return index

# Step 4: Retrieval function
def retrieve_similar_qa(query, vectorizer, index, qa_df, k=5):
    """Retrieve top-k similar Q&A pairs based on user query."""
    # Clean and embed the query
    query_clean = clean_text(query)
    query_embedding = vectorizer.transform([query_clean]).toarray()
    
    # Search the index
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    results = []
    for i in range(min(k, len(indices[0]))):
        idx = indices[0][i]
        if idx < len(qa_df):
            results.append({
                'question': qa_df['Question'].iloc[idx],
                'answer': qa_df['Answer'].iloc[idx],
                'distance': float(distances[0][i])
            })
    
    return results

# Main execution
if __name__ == "__main__":
    # Load data
    csv_file = 'university_qa.csv'
    df = load_and_preprocess_data(csv_file)
    
    # Get cleaned questions for embedding
    questions = df['Question'].apply(clean_text).tolist()
    
    # Create embeddings
    vectorizer, embeddings = create_embeddings(questions)
    
    # Create and save FAISS index
    index = create_faiss_index(embeddings)
    
    # Test retrieval
    print("\n--- Testing Retrieval ---")
    test_queries = [
        "What programs are available?",
        "When is the admission deadline?",
        "How much is the tuition fee?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retrieve_similar_qa(query, vectorizer, index, df, k=3)
        for r in results:
            print(f"  Q: {r['question']}")
            print(f"  A: {r['answer']}")
            print(f"  Distance: {r['distance']:.4f}")
    
    print("\n✓ Indexing complete! Ready for Flask app.")