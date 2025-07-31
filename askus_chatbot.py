import requests
from bs4 import BeautifulSoup
import time
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Crawl FAQs from AskUs site
# -----------------------------
def crawl_askus_faq(keyword="enrol", max_pages=3, sleep_sec=1):
    base_url = "https://askus.utas.edu.au"
    search_url = f"{base_url}/app/answers/list/kw/{keyword}/page/{{page}}"
    headers = {"User-Agent": "Mozilla/5.0"}
    faq_data = []

    # Use session to maintain headers and cookies
    session = requests.Session()
    session.headers.update(headers)

    # Create a folder to save raw HTML for debugging
    os.makedirs("html_debug", exist_ok=True)

    for page in range(1, max_pages + 1):
        print(f"📥 Crawling page {page}...")
        try:
            res = session.get(search_url.format(page=page), timeout=10)
            html_path = f"html_debug/page_{page}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(res.text)

            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.select("a[href*='/app/answers/detail/']")

            print(f"🔎 Found {len(links)} FAQ links on page {page}")
            if len(links) == 0:
                print(f"⚠️ Page structure might have changed. Saved HTML to {html_path}")

            for link in links:
                title = link.text.strip()
                href = base_url + link.get("href")
                print(f"🔗 Fetching: {title}")
                detail = session.get(href, timeout=10)
                detail_soup = BeautifulSoup(detail.text, 'html.parser')
                answer_div = detail_soup.select_one(".answer_text")
                answer = answer_div.get_text(strip=True) if answer_div else ""
                faq_data.append({
                    "question": title,
                    "answer": answer,
                    "url": href
                })
                time.sleep(sleep_sec)

        except Exception as e:
            print(f"❌ Failed to fetch page {page}: {e}")
    
    # Save all scraped data into a local JSON file
    with open("faq_data.json", "w", encoding="utf-8") as f:
        json.dump(faq_data, f, indent=2, ensure_ascii=False)
    
    print("✅ FAQ data saved to faq_data.json")
    return faq_data

# -----------------------------
# Load JSON data from file
# -----------------------------
def load_faq_data():
    with open("faq_data.json", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# Search FAQ using TF-IDF
# -----------------------------
def search_faq(user_query, data, top_n=1):
    def normalize(text):
        return text.lower().replace("enroll", "enrol")  # US to UK spelling fix

    # Combine question and answer for semantic search
    documents = [
        normalize(item["question"] + " " + item["answer"])
        for item in data if item["question"].strip()
    ]
    user_query = normalize(user_query)

    if not documents:
        raise ValueError("❌ No valid FAQ entries found.")

    vectorizer = TfidfVectorizer().fit(documents + [user_query])
    doc_vecs = vectorizer.transform(documents)
    user_vec = vectorizer.transform([user_query])
    sims = cosine_similarity(user_vec, doc_vecs).flatten()
    top_indices = sims.argsort()[-top_n:][::-1]
    return [data[i] for i in top_indices]

# -----------------------------
# Main interactive console loop
# -----------------------------
def main():
    print("📚 UTAS AskUs FAQ Chatbot (Console + Debug)")
    choice = input("Do you want to re-crawl FAQ data? (y/n): ").strip().lower()
    if choice == 'y':
        data = crawl_askus_faq(keyword="enrol", max_pages=3)
    else:
        data = load_faq_data()

    if not data:
        print("❌ FAQ data is empty. Please check html_debug folder for debugging.")
        return

    while True:
        query = input("\nWhat is your question? (type 'exit' to quit)\n> ")
        if query.lower() == "exit":
            break
        try:
            results = search_faq(query, data)
            if results:
                res = results[0]
                print("\n✅ Best matched question:", res["question"])
                print("📖 Answer preview:", res["answer"][:300] + "..." if len(res["answer"]) > 300 else res["answer"])
                print("🔗 URL:", res["url"])
            else:
                print("❌ No relevant FAQ found.")
        except Exception as e:
            print("⚠️ Error:", e)

if __name__ == "__main__":
    main()
