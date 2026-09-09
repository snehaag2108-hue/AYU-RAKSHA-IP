from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document

from app.core.config import settings


def extract_text(
    path: str
) -> str:

    file_path = Path(path)

    extension = (
        file_path.suffix.lower()
    )


    if extension == ".pdf":

        reader = PdfReader(
            str(file_path)
        )

        pages = []

        for page in reader.pages:

            pages.append(
                page.extract_text()
                or ""
            )

        return "\n".join(
            pages
        )


    if extension == ".docx":

        document = Document(
            str(file_path)
        )

        return "\n".join(
            paragraph.text
            for paragraph
            in document.paragraphs
        )


    return file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def save_document_as_knowledge(
    text: str,
    title: str,
    authority="User Upload"
):

    knowledge_dir = Path(
        settings.knowledge_dir
    )

    knowledge_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    safe_title = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in title
    )[:80]


    output_file = (
        knowledge_dir /
        f"upload_{safe_title}.json"
    )


    import json


    record = {

        "id":
            f"upload-{safe_title}",

        "title":
            title,

        "type":
            "user_upload",

        "authority":
            authority,

        "jurisdiction":
            "User supplied",

        "version":
            "user-upload",

        "source_url":
            None,

        "text":
            text[:50000]

    }


    output_file.write_text(

        json.dumps(
            [record],
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"
    )


    return output_file
