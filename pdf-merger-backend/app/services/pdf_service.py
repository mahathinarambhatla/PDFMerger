"""PDF service layer.

Contains business logic for merging uploaded PDFs.
"""

from pypdf import PdfWriter
import io


def merge_pdfs(files):
    writer = PdfWriter()

    for file in files:
        file.stream.seek(0)
        writer.append(file.stream)

    output = io.BytesIO()
    writer.write(output)
    writer.close()

    output.seek(0)

    return output