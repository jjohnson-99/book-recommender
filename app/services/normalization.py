import re
from typing import Optional


def normalize_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None

    text = text.lower()

    # remove punctuation except spaces
    text = re.sub(r"[^\w\s]", "", text)

    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_author(author: Optional[str]) -> Optional[str]:
    author = author.strip()

    if "," in author:
        parts = [p.strip() for p in author.split(",")]

        if len(parts) >= 2:
            # handle "Last, First Middle"
            last = parts[0]
            first = " ".join(parts[1:])
            author = f"{first} {last}"

    return author


def canonical_author(author: Optional[str]) -> Optional[str]:
    author = normalize_author(author)
    author = normalize_text(author)
    return author
