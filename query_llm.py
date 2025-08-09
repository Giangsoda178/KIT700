import requests
import re
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# === Configuration ===
GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_API_KEY  = "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"
CHROMA_DIR    = "chroma_db"
EMBED_MODEL   = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL     = "llama3-70b-8192"
COLLECTION_NAME = "course_info"

# === Load embedding + Chroma ===
embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
db = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embedding,
    collection_name=COLLECTION_NAME
)

# === Suggestion display ===
suggestions = [
    "What can I learn in Master of Information Communication and Technology?"
]

print("\n📘 Ask about UTAS courses (type 'exit' to quit)")
print("💡 Suggestions:")
for s in suggestions:
    print("  -", s)

# === Query loop ===
while True:
    query = input("\n❓ Your question: ")
    if query.lower() == "exit":
        break

    # Step 1: Retrieve from Chroma
    results = db.similarity_search(query, k=4)
    context_texts = "\n\n---\n\n".join([doc.page_content for doc in results])

    # Step 2: Build prompt for LLaMA
    prompt = f"""
        You are a helpful assistant answering questions about University of Tasmania courses based on the provided context.

        Context from course database:
        {context_texts}

        Question: {query}

        Based *only* on the context provided, answer the question clearly and concisely. If the context doesn't contain the answer, say "I'm sorry, I don't have enough information to answer that question. Please check the UTAS website (www.utas.edu.au) for more information."
        """

    # Step 3: Call Groq API
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a course information assistant for the University of Tasmania."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }

    response = requests.post(
        f"{GROQ_API_BASE}/chat/completions",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        # Post-process to remove conversational filler if the model adds it
        answer = re.sub(r"Based on the context provided, here is the answer to your question:\n+", "", answer).strip()
        print("\n💬 Answer:", answer)
    else:
        print("❌ Error:", response.text)