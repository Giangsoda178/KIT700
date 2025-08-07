from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

# Configure headless browser
options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Setup ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Load the page
url = "https://www.utas.edu.au/courses/cse/courses/k7i-master-of-information-technology-and-systems?year=2026"
driver.get(url)

# Click each accordion heading to expand content
#accordion_headers = driver.find_elements(By.CLASS_NAME, "js-accordion-heading")
#for header in accordion_headers:
#    try:
#        header.click()
#        time.sleep(0.5)  # Small delay for animation/DOM update
#    except Exception as e:
#        print(f"❌ Error clicking accordion: {e}")

# Now parse the fully loaded HTML
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Extract title
course_data = {
    "title": "",
    "overview": "",
    "duration": "",
    "course_objectives": "",
    "learning_outcomes": "",
    "practical_experience": "",
    "work_placement": "",
    "career_outcomes": "",
    "course_structure": "",
    "entry_requirements": "",
    "fees": ""
}

title_tag = soup.find('h1', class_='l-object-page-header--page-title')
if title_tag:
    title_text = title_tag.contents[0].strip()
    code_text = title_tag.find('small').get_text(strip=True) if title_tag.find('small') else ""
    course_data["title"] = f"{title_text} {code_text}"

overview_block = soup.select_one("div.richtext.richtext__medium")
overview_text = overview_block.get_text(separator="\n", strip=True) if overview_block else "N/A"
course_data["overview"] = overview_text

duration_tag = soup.find('dd', class_='meta-list--item__time')
if duration_tag:
    duration_text = duration_tag.find('span', class_='meta-list--item-inner').contents[0].strip()
    course_data["duration"] = duration_text


def extract_section_text(soup, section_id):
    section_div = soup.find("div", id=section_id)
    if section_div:
        content_div = section_div.find("div", class_="richtext richtext__medium")
        if content_div:
            return content_div.get_text(separator="\n", strip=True)
        else:
            return section_div.get_text(separator="\n", strip=True)
    return "N/A"

course_data["course_objectives"] = extract_section_text(soup, "course-objectives")
course_data["learning_outcomes"] = extract_section_text(soup, "learning-outcomes")
course_data["practical_experience"] = extract_section_text(soup, "practical-experience")
course_data["work_placement"] = extract_section_text(soup, "opportunities-abroad")


def extract_section_by_heading_id(soup, heading_id):
    heading = soup.find(['h2', 'h3'], id=heading_id)
    if heading:
        content = heading.find_next('div', class_='richtext richtext__medium')
        if content:
            return content.get_text(separator="\n", strip=True)
    return "N/A"

course_data["career_outcomes"] = extract_section_by_heading_id(soup, "career-outcomes")
course_data["course_structure"] = extract_section_by_heading_id(soup, "course-structure")


entry_requirements = {}
entry_requirements_header = soup.find("h2", id="entry-requirements")

if entry_requirements_header:
    # The container div follows the h2
    entry_container = entry_requirements_header.find_next("div", class_="block block__pad-lg block__shadowed")
    if entry_container:
        accordion_sections = entry_container.find_all("section", class_="accordion--panel")
        
        for section in accordion_sections:
            # Get the section title (e.g., "For Domestic students")
            title_tag = section.find("a", class_="requirements accordion--link")
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"

            # Get the accordion body content
            content_div = section.find("div", class_="accordion--content")
            content = content_div.get_text(separator="\n", strip=True) if content_div else ""

            # Save to dictionary
            entry_requirements[title] = content

course_data["entry_requirements"] = entry_requirements

fees = {}
fees_header = soup.find("h2", id="fees-and-scholarships")

if fees_header:
    fees_container = fees_header.find_next("div", class_="block block__pad-lg block__shadowed")
    if fees_container:
        fees_sections = fees_container.find_all("section", class_="sectioned-content")

        for section in fees_sections:
            title_tag = section.find("h4", class_="sectioned-content--title")
            content_div = section.find("div", class_="richtext richtext__medium")
            if not title_tag or not content_div:
                continue

            title = title_tag.get_text(strip=True)
            content = content_div.get_text(separator="\n", strip=True)

            if "International" in title:
                if title not in fees:
                    fees[title] = content
                else:
                    fees[title] += "\n\n" + content  # Append additional content
            else:
                fees[title] = content

course_data["fees"] = fees

with open('course_data.json', 'w', encoding='utf-8') as f:
    json.dump(course_data, f, indent=4, ensure_ascii=False)

print("✅ Data saved to course_data.json")
