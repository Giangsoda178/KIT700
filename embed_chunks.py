import json
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import re

# ---------- SETTINGS ----------
JSON_FILE = "course_data.json"  # Your JSON file path
CHROMA_DIR = "chroma_db"    # Local storage directory
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "course_info"

# ---------- STEP 1: Load JSON ----------
with open(JSON_FILE, "r", encoding="utf-8") as f:
    course_data = json.load(f)

# ---------- STEP 2: Create Documents from JSON structure ----------
documents = []
course_title = course_data.get("title", "Unknown Course")

# Add top-level course information as separate documents
for key, value in course_data.items():
    if isinstance(value, str):
        # Clean up the text by removing excessive newlines and spaces
        clean_value = re.sub(r'\s+', ' ', value).strip()
        documents.append(
            Document(
                page_content=f"{key.replace('_', ' ').title()}: {clean_value}",
                metadata={"source": key, "title": course_title},
            )
        )

# Recursively add nested dicts in entry_requirements and fees
def flatten_nested_text(d, parent_key=""):
    docs = []
    for k, v in d.items():
        key_name = f"{parent_key} - {k}" if parent_key else k
        if isinstance(v, str):
            clean_value = re.sub(r'\s+', ' ', v).strip()
            docs.append(Document(
                page_content=f"{key_name.replace('_', ' ').title()}: {clean_value}",
                metadata={"source": key_name, "title": course_title}
            ))
        elif isinstance(v, dict):
            docs.extend(flatten_nested_text(v, key_name))
    return docs

documents.extend(flatten_nested_text(course_data.get("entry_requirements", {})))
documents.extend(flatten_nested_text(course_data.get("fees", {})))

# Process the nested course structure for units
course_structure = course_data.get("course_structure", {})
for section_title, units in course_structure.items():
    if isinstance(units, list):
        for unit in units:
            if isinstance(unit, dict):
                # Combine all relevant unit details into a single text block
                content_parts = [
                    f"Unit Title: {unit.get('unit_title', 'N/A')}",
                    f"Unit Code: {unit.get('unit_code', 'N/A')}",
                    f"Credit Points: {unit.get('unit_credit_points', 'N/A')}",
                    f"Description: {unit.get('unit_description', 'N/A')}"
                ]
                
                # Add availability details
                availability_info = []
                for availability in unit.get("unit_availability", []):
                    if isinstance(availability, dict):
                        location = availability.get('Location', 'N/A')
                        period = availability.get('Study period', 'N/A')
                        attendance = availability.get('Attendance options 1', '')
                        availability_info.append(f"- {location} ({period}): {attendance}")
                
                if availability_info:
                    content_parts.append("Availability:\n" + "\n".join(availability_info))

                # Create the final page content
                page_content = "\n".join(content_parts)
                
                documents.append(
                    Document(
                        page_content=page_content,
                        metadata={
                            "source": f"unit-{unit.get('unit_code', 'N/A')}",
                            "title": course_title,
                            "section": section_title
                        },
                    )
                )

# ---------- STEP 3: Create embeddings & store in Chroma ----------
embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# Clear the collection if it already exists to avoid duplicates
# Note: This is a simple approach. For production, you might want a more sophisticated update strategy.
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
