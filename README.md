# KIT700 ChatBot

## 📘 Unit Outline Chunk Extractor & Embedding Generator

This Python script extracts key sections from a UTAS Unit Outline PDF, generates sentence embeddings using a transformer model, and saves the result as a structured JSON file — ready for vector database ingestion.

---

## ✅ What it does

- Extracts text from a Unit Outline PDF  
- Splits it into chunks based on predefined section titles  
- Generates embeddings using `all-MiniLM-L6-v2` from Sentence Transformers  
- Saves each chunk with metadata to `unit_chunks/chunks.json`  

---

## 📦 Requirements

Make sure you have the following installed in your virtual environment:

```bash
conda create -n kit700-env python=3.10
conda activate kit700-env
conda install -c conda-forge pdfminer.six
```

# 📁 File Structure

project/
├── Unit Outline.pdf         # Your input PDF file  
├── pdf.py                   # The main script  
├── unit_chunks/
│   └── chunks.json



# 🚀 How to Run

python pdf.py
After successful execution, you will see output like:

✅ Successfully saved 7 chunks to unit_chunks/chunks.json

## 🛠 Parameters (Optional)

To adapt this script to other units:

Replace Unit Outline.pdf with your actual PDF filename
Change unit_code = "KIT514" in pdf.py accordingly

# 🧠 Embedding Model Used

all-MiniLM-L6-v2
Lightweight & fast
Suitable for semantic chunk comparison and vector search
