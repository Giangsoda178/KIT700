import json
import re
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# ---------- SETTINGS ----------
JSON_FILE = "course_data.json"  # Your JSON file path
CHROMA_DIR = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "course_info"

# ---------- STEP 1: Load JSON ----------
with open(JSON_FILE, "r", encoding="utf-8") as f:
    course_data = json.load(f)

course_title = course_data.get("title", "Unknown Course")
documents = []

# ---------- STEP 2: Flattening logic ----------
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def flatten_dict(d, parent_key=""):
    docs = []
    for k, v in d.items():
        key_name = f"{parent_key} - {k}" if parent_key else k
        if isinstance(v, str):
            docs.append(Document(
                page_content=f"{key_name.replace('_', ' ').title()}: {clean_text(v)}",
                metadata={"source": key_name, "title": course_title}
            ))
        elif isinstance(v, dict):
            docs.extend(flatten_dict(v, key_name))
        elif isinstance(v, list):
            for idx, item in enumerate(v, 1):
                if isinstance(item, dict):
                    docs.extend(flatten_dict(item, f"{key_name} [{idx}]"))
                else:
                    docs.append(Document(
                        page_content=f"{key_name} [{idx}]: {clean_text(str(item))}",
                        metadata={"source": key_name, "title": course_title}
                    ))
    return docs

# ---------- STEP 3: Add top-level strings ----------
for key, value in course_data.items():
    if isinstance(value, str):
        documents.append(Document(
            page_content=f"{key.replace('_', ' ').title()}: {clean_text(value)}",
            metadata={"source": key, "title": course_title}
        ))

# ---------- STEP 4: Flatten nested dicts ----------
if "entry_requirements" in course_data:
    documents.extend(flatten_dict(course_data["entry_requirements"], "Entry Requirements"))

if "fees" in course_data:
    documents.extend(flatten_dict(course_data["fees"], "Fees"))

# ---------- STEP 5: Flatten course_structure with category ----------
if "course_structure" in course_data:
    for section_title, units in course_data["course_structure"].items():
        for unit in units:
            unit_parts = [
                f"Category: {section_title}",  # include category name in the searchable text
                f"Unit Title: {unit.get('unit_title', 'N/A')}",
                f"Unit Code: {unit.get('unit_code', 'N/A')}",
                f"Credit Points: {unit.get('unit_credit_points', 'N/A')}",
                f"Description: {clean_text(unit.get('unit_description', 'N/A'))}"
            ]
            # Add availability info
            availability_info = []
            for availability in unit.get("unit_availability", []):
                if isinstance(availability, dict):
                    location = availability.get("Location", "N/A")
                    period = availability.get("Study period", "N/A")
                    attendance = availability.get("Attendance options 1", "")
                    availability_info.append(f"- {location} ({period}): {attendance}")
            if availability_info:
                unit_parts.append("Availability:\n" + "\n".join(availability_info))

            documents.append(Document(
                page_content="\n".join(unit_parts),
                metadata={
                    "source": f"unit-{unit.get('unit_code', 'N/A')}",
                    "title": course_title,
                    "category": section_title  # this makes filtering by category possible
                }
            ))


# ---------- STEP 6: Create embeddings & store in Chroma ----------
embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

try:
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding, collection_name=COLLECTION_NAME)
    db.delete_collection()
    print(f"🧹 Cleared existing collection '{COLLECTION_NAME}'.")
except Exception as e:
    print(f"Collection '{COLLECTION_NAME}' does not exist or another error occurred: {e}. A new one will be created.")

db = Chroma.from_documents(
    documents=documents,
    embedding=embedding,
    persist_directory=CHROMA_DIR,
    collection_name=COLLECTION_NAME
)
db.persist()

print(f"✅ Stored {len(documents)} chunks in vector DB at '{CHROMA_DIR}'")
