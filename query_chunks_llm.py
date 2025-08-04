import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

# ====== Groq API Setup ======
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="GROQ_API_KEY"
)

# ====== Load embedding model ======
model = SentenceTransformer("all-MiniLM-L6-v2")

# ====== Load chunked unit content ======
with open("unit_chunks/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# ====== Get user input ======
query = input("📘 Enter your question (e.g., what will I learn in KIT514?):\n> ")
query_vec = model.encode([query])

# ====== Compute similarity ======
scores = []
for chunk in chunks:
    chunk_vec = np.array(chunk["embedding"])
    score = cosine_similarity([chunk_vec], query_vec)[0][0]
    scores.append((score, chunk["unit"], chunk["chunk_title"], chunk["text"]))

top_k = sorted(scores, key=lambda x: x[0], reverse=True)[:3]

# ====== Construct context ======
context = "\n\n".join(
    f"{title} ({unit}):\n{text.strip()}"
    for _, unit, title, text in top_k
)

# ====== LLM Prompt ======
prompt = f"""You are a helpful assistant at UTAS. Use the following course unit context to answer the user's question clearly and accurately.

Context:
{context}

Question: {query}

Answer:"""

# ====== Query Groq (LLaMA3) ======
response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {"role": "system", "content": "You are a helpful UTAS course assistant."},
        {"role": "user", "content": prompt}
    ]
)

print("\n💡 Answer from LLM:\n")
print(response.choices[0].message.content)
