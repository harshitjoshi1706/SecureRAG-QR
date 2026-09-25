import fitz


def extract_text_from_pdf(file_path: str) -> dict:
    document = fitz.open(file_path)

    full_text = ""
    pages = []

    for page_number in range(len(document)):
        page = document[page_number]
        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

        full_text += text + "\n"

    document.close()

    return {
        "page_count": len(pages),
        "text": full_text,
        "pages": pages
    }