from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf(file):
    """
    Extract text from every page of a PDF.
    """

    reader = PdfReader(
        BytesIO(file.getvalue())
    )

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)


def extract_text_from_txt(file):
    """
    Extract text from a TXT file.
    """

    return file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )


def extract_text(file):
    """
    Detect the file type and extract its text.
    """

    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)

    elif filename.endswith(".txt"):
        return extract_text_from_txt(file)

    else:
        raise ValueError(
            "ASTRA currently supports only PDF and TXT files."
        )