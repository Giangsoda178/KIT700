# KIT700 ChatBot

# Files we play around at week3

You can edit `pdf2chunksss.py` to add more unit outlines.

Then run `query_chunks_llm.py` to ask questions and get answer.(you need to change the groq api key to your own key)

```bash
pdf2chunksss.py
query_chunks_llm.py
```


You can scrab more pages by editing code and ask questions
```bash
askus_chatbot.py
```

# Part1 📘 Unit Outline Chunk Extractor & Embedding Generator

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
conda install requests beautifulsoup4 scikit-learn              
```

# 📁 File Structure

project/

├── Unit Outline.pdf               # Your input PDF file  

├── pdf2chunk.py                   # The main script  

├── unit_chunks/

│   └── chunks.json



## 🚀 How to Run

```bash
python pdf2chunk.py
```

After successful execution, you will see output like:

✅ Successfully saved 7 chunks to unit_chunks/chunks.json

```bash
python query_chunks.py
```

You can ask a simple question like: 
```bash
what can I learn from kit514
```

or 

```bash
what are the assignment in kit514
```

It will lets you run top-3 retrieval.

## 🛠 Parameters (Optional)

To adapt this script to other units:

Replace Unit Outline.pdf with your actual PDF filename
Change unit_code = "KIT514" in pdf.py accordingly



# 🧠 Embedding Model Used

all-MiniLM-L6-v2

Lightweight & fast

Suitable for semantic chunk comparison and vector search
