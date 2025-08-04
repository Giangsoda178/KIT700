import os
import re
import json
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer

# ---------- Step 1: Configuration ----------
input_dir = "unit_pdfs"  # folder where multiple PDFs are stored
output_dir = "unit_chunks"
output_path = os.path.join(output_dir, "chunks.json")

field_titles = [
    "Contact Details",
    "Unit Description",
    "Intended Learning Outcomes",
    "Teaching Arrangements",
    "Engagement Expectations",
    "Assessment Schedule",
    "Assessment Details"
]

model = SentenceTransformer("all-MiniLM-L6-v2")
all_chunks = []

# ---------- Step 2: Text splitting function ----------
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

# ---------- Step 3: Process each PDF ----------
os.makedirs(output_dir, exist_ok=True)
pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]

for filename in pdf_files:
    pdf_path = os.path.join(input_dir, filename)
    print(f"📄 Processing: {filename}")
    text = extract_text(pdf_path)

    # Extract unit code from filename (e.g. "KIT514 Unit Outline.pdf" → "KIT514")
    match = re.search(r"(KIT\d{3})", filename.upper())
    unit_code = match.group(1) if match else "UNKNOWN"

    chunks = extract_sections(text, field_titles)
    for chunk in chunks:
        embedding = model.encode(chunk["text"]).tolist()
        chunk["unit"] = unit_code
        chunk["embedding"] = embedding
        all_chunks.append(chunk)

# ---------- Step 4: Save merged result ----------
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(all_chunks)} chunks from {len(pdf_files)} PDFs to {output_path}")
