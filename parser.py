import sys
import json
import fitz  # PyMuPDF

def contains_digit(text):
    return any(char.isdigit() for char in text)

def extract_chapters(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()  # Table of contents: [level, title, page]

    chapter_markers = []  # (page_number, chapter_title)

    # Identify top-level TOC entries that are likely chapter headings
    for entry in toc:
        level, title, page = entry
        if level <= 1 and (contains_digit(title) or "chapter" in title.lower()):
            chapter_markers.append((page, title))

    original_len = len(chapter_markers)
    found_end = False
    for entry in toc:
        level, title, page = entry
        if found_end and level <= 1:
            chapter_markers.append((page, "END"))
            break
        if chapter_markers and chapter_markers[-1][1] == title:
            found_end = True

    if len(chapter_markers) == original_len:
        chapter_markers.append((doc.page_count, "END"))

    chapters = []
    for i in range(len(chapter_markers) - 1):
        start_page = chapter_markers[i][0]
        end_page = chapter_markers[i + 1][0]
        title = chapter_markers[i][1]
        
        chapter_text = ""
        for page_num in range(start_page - 1, end_page - 1):
            chapter_text += doc[page_num].get_text()

        chapters.append({
            "id": i,
            "title": title,
            "content": chapter_text.strip()
        })

    return { "chapters": chapters }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({ "error": "Usage: python parser.py <pdf_path>" }))
        sys.exit(1)

    pdf_path = sys.argv[1]
    try:
        result = extract_chapters(pdf_path)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({ "error": str(e) }))
        sys.exit(1)

if __name__ == "__main__":
    main()
