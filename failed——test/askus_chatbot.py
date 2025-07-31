import requests
from bs4 import BeautifulSoup
import time
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- Step 1: Crawl FAQ --------
def crawl_askus_faq(keyword="enrol", max_pages=3, sleep_sec=1):
    base_url = "https://askus.utas.edu.au"
    search_url = f"{base_url}/app/answers/list/kw/{keyword}/page/{{page}}"
    headers = {"User-Agent": "Mozilla/5.0"}
    faq_data = []

    for page in range(1, max_pages + 1):
        print(f"📥 Crawling page {page}...")
        try:
            res = requests.get(search_url.format(page=page), headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.select("div.answer_text a[href*='/app/answers/detail/']")

            if not links:
                print("⚠️ 没有找到任何链接，可能被重定向或页面为空。")

            for link in links:
                title = link.text.strip()
                href = base_url + link.get("href")
                print(f"🔗 抓取问题：{title}")
                detail = requests.get(href, headers=headers, timeout=10)
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
            print(f"⚠️ 页面 {page} 抓取失败：{e}")
    
    with open("faq_data.json", "w") as f:
        json.dump(faq_data, f, indent=2, ensure_ascii=False)
    print("✅ FAQ 数据已保存至 faq_data.json")
    return faq_data

# -------- Step 2: TF-IDF 检索 --------
def load_faq_data():
    with open("faq_data.json") as f:
        return json.load(f)

def search_faq(user_query, data, top_n=1):
    questions = [item["question"] for item in data if item["question"].strip()]
    if not questions:
        raise ValueError("❌ FAQ 数据中没有有效问题文本。")

    vectorizer = TfidfVectorizer().fit(questions + [user_query])
    q_vecs = vectorizer.transform(questions)
    user_vec = vectorizer.transform([user_query])
    sims = cosine_similarity(user_vec, q_vecs).flatten()
    top_indices = sims.argsort()[-top_n:][::-1]
    return [data[i] for i in top_indices]

# -------- Step 3: Console Chatbot --------
def main():
    print("📚 UTAS AskUs FAQ Chatbot (Console)")
    choice = input("是否需要重新抓取 FAQ 数据？(y/n): ").strip().lower()
    if choice == 'y':
        data = crawl_askus_faq(keyword="enrol", max_pages=3)
    else:
        data = load_faq_data()

    if not data:
        print("❌ FAQ 数据为空，请检查网络或重新爬取。")
        return

    while True:
        query = input("\n你想问什么？(输入 'exit' 退出)\n> ")
        if query.lower() == "exit":
            break
        try:
            results = search_faq(query, data)
            if results:
                res = results[0]
                print("\n✅ 最相关的问题：", res["question"])
                print("📖 回答预览：", res["answer"][:300] + "..." if len(res["answer"]) > 300 else res["answer"])
                print("🔗 链接：", res["url"])
            else:
                print("❌ 没有找到相关问题。")
        except Exception as e:
            print("⚠️ 错误：", e)

if __name__ == "__main__":
    main()
