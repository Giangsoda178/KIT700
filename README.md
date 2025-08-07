# KIT700 ChatBot

# 🆕 Files we play around at week3

### Code will be updated at the end of week with full json files

You can edit `pdf2chunksss.py` to add more unit outlines.

Then run `query_chunks_llm.py` to ask questions and get answer.(You need to get your own API key on Groq)

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

If you can not use system python like me

Make sure you have the following installed in your virtual environment:

```bash
conda create -n kit700-env python=3.10
conda activate kit700-env
conda install -c conda-forge pdfminer.six
conda install requests beautifulsoup4 scikit-learn
```

```bash
pip install pdfminer.six
pip install sentence-transformers
pip install numpy
pip install scikit-learn
pip install openai
```

# 📁 File Structure

project/

├── unit_pdfs # Your input PDF file folder

├── pdf2chunksss.py # The main script 1

├── query_chunks_llm.py # The main script 2

├── unit_chunks/

│ └── chunks.json

## 🚀 How to Run

You might can use `python pdf2chunksss.py` to run if you are using system python.

```bash
/opt/anaconda3/envs/kit700-env/bin/python pdf2chunksss.py
```

After successful execution, you will see the chunks in `unit_chunks/chunks.json`

```bash
/opt/anaconda3/envs/kit700-env/bin/python query_chunks_llm.py
```

You can ask a simple question like:

```bash
what can I learn from kit514
```

or

```bash
what are the assignment in kit514
```

It will give you an answer

# 🧠 Embedding Model Used

all-MiniLM-L6-v2

Lightweight & fast

Suitable for semantic chunk comparison and vector search
