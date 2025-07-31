import os
import re
import json
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer

# ---------- Step 1: Extract text from the PDF ----------
pdf_path = "Unit Outline.pdf"
unit_code = "KIT514"  # Can be parameterized or auto-detected

text = extract_text(pdf_path)

# ---------- Step 2: Split text into sections by predefined fields ----------
field_titles = [
    "Contact Details",
    "Unit Description",
    "Intended Learning Outcomes",
    "Teaching Arrangements",
    "Engagement Expectations",
    "Assessment Schedule",
    "Assessment Details"
]

def extract_sections(text, titles):
    results = []
    lower_text = text.lower()
    positions = []

    for title in titles:
        match = re.search(re.escape(title.lower()), lower_text)
        if match:
            positions.append((title, match.start()))

    positions.sort(key=lambda x: x[1])

    for i in range(len(positions)):
        title, start = positions[i]
        end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        content = text[start:end].replace("\n", " ").strip()
        results.append({"chunk_title": title, "text": content})
    return results

chunks = extract_sections(text, field_titles)

# ---------- Step 3: Generate sentence embeddings ----------
model = SentenceTransformer("all-MiniLM-L6-v2")
for chunk in chunks:
    embedding = model.encode(chunk["text"]).tolist()
    chunk["unit"] = unit_code
    chunk["embedding"] = embedding

# ---------- Step 4: Save the result to a JSON file ----------
output_dir = "unit_chunks"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "chunks.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"✅ Successfully saved {len(chunks)} chunks to {output_path}")
