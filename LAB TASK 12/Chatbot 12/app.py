"""
University QnA Bot - Flask Application
Uses FAISS vector similarity search for intelligent question answering.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import re
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

app = Flask(__name__)

# Global variables to store the model and data
vectorizer = None
index = None
qa_df = None

def clean_text(text):
    """Clean text by removing symbols and converting to lowercase."""
    if isinstance(text, str):
        text = re.sub(r'[^A-Za-z\s]', '', text)
        text = text.lower().strip()
    else:
        text = ''
    return text

def initialize_qa_system():
    """Initialize the QnA system by loading the FAISS index and data."""
    global vectorizer, index, qa_df
    
    # Load the Q&A data
    qa_df = pd.read_csv('university_qa.csv')
    qa_df = qa_df.dropna()
    
    # Recreate the vectorizer and fit on the questions
    questions = qa_df['Question'].apply(clean_text).tolist()
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=500,
        stop_words='english'
    )
    vectorizer.fit(questions)
    
    # Load the FAISS index
    index = faiss.read_index('qa_faiss.index')
    
    print("QnA system initialized successfully!")

def retrieve_answer(query, k=1):
    """Retrieve the most similar Q&A pair based on user query."""
    # Clean and embed the query
    query_clean = clean_text(query)
    query_embedding = vectorizer.transform([query_clean]).toarray()
    
    # Search the FAISS index
    distances, indices = index.search(query_embedding.astype('float32'), k)
    
    # Get the top result
    if len(indices[0]) > 0:
        idx = indices[0][0]
        if idx < len(qa_df):
            answer = qa_df['Answer'].iloc[idx]
            return answer
    
    return "I'm sorry, I couldn't find a relevant answer to your question."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    user_message = request.form["msg"]
    
    # Get answer from FAISS-based retrieval
    answer = retrieve_answer(user_message)
    
    return jsonify({"reply": answer})

# Initialize on startup
initialize_qa_system()

if __name__ == "__main__":
    app.run(debug=True)