import fitz
#fitz is python module provided by PyMuPDF, a library for PDF processing
#Its job here is to open and read PDF files.

def extract_text_from_pdf(file_path: str) -> dict: #Here we define a function that takes a file path as input and returns a dictionary containing the extracted text and page information from the PDF.
    document = fitz.open(file_path)

    full_text = "" #empty string to store the full text of the PDF
    pages = [] #list to store the text of each page along with its page number

    for page_number in range(len(document)): #Iterate through each page in the PDF document
        page = document[page_number] #Get the page object
        text = page.get_text() #Extract the text from the page using the get_text() method provided by PyMuPDF

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

        full_text += text + "\n"

    document.close() #Close the PDF document to free up resources

    return {
        "page_count": len(pages),
        "text": full_text,
        "pages": pages
    }