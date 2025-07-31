import re
import json
from pdfminer.high_level import extract_text

# Step 1: 提取 PDF 文本
pdf_path = "Unit Outline.pdf"
text = extract_text(pdf_path)

# Step 2: 定义字段及其可能的正则表达式关键词（不区分大小写）
field_patterns = {
    "Contact Details": r"(?i)Contact\s+Details",
    "Unit Description": r"(?i)Unit\s+Description",
    "Intended Learning Outcomes": r"(?i)Intended\s+Learning\s+Outcomes",
    "Teaching Arrangements": r"(?i)Teaching\s+Arrangements",
    "Engagement Expectations": r"(?i)Engagement\s+Expectations",
    "Assessment Schedule": r"(?i)Assessment\s+Schedule",
    "Assessment Details": r"(?i)Assessment\s+Details"
}

# Step 3: 提取每个字段的起始位置
def find_field_positions(text, pattern_dict):
    positions = []
    for field, pattern in pattern_dict.items():
        match = re.search(pattern, text)
        if match:
            positions.append((field, match.start()))
    return sorted(positions, key=lambda x: x[1])

# Step 4: 根据起始位置提取字段段落
def extract_sections(text, field_patterns):
    results = {}
    positions = find_field_positions(text, field_patterns)

    for i in range(len(positions)):
        field, start = positions[i]
        end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        content = text[start:end].replace("\n", " ").strip()
        results[field] = content

    return results

# Step 5: 提取字段内容并输出
extracted_fields = extract_sections(text, field_patterns)
print(json.dumps(extracted_fields, indent=2, ensure_ascii=False))


# Step 6: 保存为 JSON 文件
with open("kit514_fields.json", "w", encoding="utf-8") as f:
    json.dump(extracted_fields, f, indent=2, ensure_ascii=False)
