import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the chunks data with pre-computed embeddings
with open("unit_chunks/chunks.json", "r") as f:
    chunks = json.load(f)

# Get user query
query = input("Enter your question (e.g., what will I learn in KIT500?):\n> ")

# Encode query into vector
query_vec = model.encode([query])

# Compute cosine similarity between query and each chunk
scores = []
for chunk in chunks:
    chunk_vec = np.array(chunk["embedding"])  # ✅ Convert to numpy array
    score = cosine_similarity([chunk_vec], query_vec)[0][0]
    scores.append((score, chunk["unit"], chunk["chunk_title"], chunk["text"]))

# Sort and display top 3 most relevant chunks
top_k = sorted(scores, key=lambda x: x[0], reverse=True)[:3]

print("\n📚 Most relevant course content chunks:\n")
for i, (score, unit, title, text) in enumerate(top_k):
    print(f"--- Top {i+1} · {unit} · {title} (score={score:.4f}) ---")
    print(text.strip())
    print()
