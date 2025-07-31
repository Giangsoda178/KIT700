# Rewriting the full test.py script with keyword-based structured chunk extraction

import os
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import json
import hashlib
import pandas as pd

# Create output directory
os.makedirs("unit_chunks", exist_ok=True)

# Unit URLs and titles
unit_links = {
    "KIT500": "https://outlines.utas.edu.au/2024/KIT/KIT500/Semester%202/KIT500_Semester%202.mhtml",
    "KIT501": "https://outlines.utas.edu.au/2025/KIT/KIT501/Semester%202/KIT501_Semester%202.mhtml",
    "KIT502": "https://outlines.utas.edu.au/2025/KIT/KIT502/Semester%202/KIT502_Semester%202.mhtml",
    "KIT503": "https://outlines.utas.edu.au/2025/KIT/KIT503/Semester%201/KIT503_Semester%201.mhtml",
}
title_map = {
    "KIT500": "Programming Foundation",
    "KIT501": "ICT Systems Administration Fundamentals",
    "KIT502": "Web Development",
    "KIT503": "ICT Professional Practices and Project Management"
}

# List of section headings to extract
SECTION_HEADINGS = [
    "Contact Details",
    "Unit Description",
    "What is the unit about?",
    "Intended Learning Outcomes",
    "Teaching Arrangements",
    "Attendance and Engagement Expectations",
    "Assessment Schedule",
    "Assessment Details",
    "Learning Resources",
    "Schedule of Learning Activities"
]

def extract_chunks_by_heading_list(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    tags = soup.find_all(['p', 'div', 'span'])

    chunks = []
    current_title = "General"
    buffer = []

    def is_heading(text):
        for heading in SECTION_HEADINGS:
            if heading.lower() in text.lower():
                return heading
        return None

    for tag in tags:
        text = tag.get_text(strip=True)
        if not text or len(text) < 4:
            continue

        matched_heading = is_heading(text)
        if matched_heading:
            if buffer:
                chunks.append({
                    "title": current_title,
                    "text": ' '.join(buffer)
                })
                buffer = []
            current_title = matched_heading
        else:
            buffer.append(text)

    if buffer:
        chunks.append({
            "title": current_title,
            "text": ' '.join(buffer)
        })

    return chunks


def main():
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    all_chunks = []

    for unit_code, url in unit_links.items():
        print(f"Processing {unit_code}")
        title = title_map.get(unit_code, "")
        response = requests.get(url)
        structured_chunks = extract_chunks_by_heading_list(response.text)

        texts = [f"{c['title']}: {c['text']}" for c in structured_chunks]
        embeddings = model.encode(texts).tolist()

        for idx, (chunk, emb) in enumerate(zip(structured_chunks, embeddings)):
            chunk_id = hashlib.md5((unit_code + str(idx)).encode()).hexdigest()
            all_chunks.append({
                "id": chunk_id,
                "unit": unit_code,
                "unit_title": title,
                "chunk_title": chunk["title"],
                "text": chunk["text"],
                "embedding": emb
            })

    # Save chunks
    with open("unit_chunks/chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"✅ Saved {len(all_chunks)} chunks to unit_chunks/chunks.json")

    # Preview
    df_preview = pd.DataFrame([{
        "unit": c["unit"],
        "title": c["chunk_title"],
        "text_snippet": c["text"][:80]
    } for c in all_chunks[:10]])
    print("\n📌 Preview of first 10 chunks:")
    print(df_preview.to_string(index=False))


if __name__ == "__main__":
    main()
