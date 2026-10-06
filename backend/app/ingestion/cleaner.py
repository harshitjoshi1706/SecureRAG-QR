import re # The re module in Python provides support for regular expressions, which are used for pattern matching and text manipulation. In this code, it is used to clean and format the extracted text from PDF files.


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n") # Replace carriage return characters with newline characters to standardize line breaks.

    text = re.sub(r"\n{3,}", "\n\n", text) # Use a regular expression to replace occurrences of three or more consecutive newline characters with just two newline characters. This helps to reduce excessive blank lines in the text.
                                            #Find 3 or more consecutive newlines and replace them with only 2 newlines.
 
    text = re.sub(r"[ \t]+", " ", text)  # Find one or more consecutive spaces or tabs. And replace them with one single space.

    return text.strip() # .strip() removes unwanted whitespace from the beginning and end of a string.