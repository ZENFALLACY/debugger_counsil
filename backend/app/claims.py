import re

from app.schemas import ExtractedClaim


FILLER_PATTERNS = (
    "i think",
    "i believe",
    "in my opinion",
    "hope this helps",
    "it seems",
    "maybe",
    "probably",
)

FACTUAL_HINTS = (
    " is ",
    " are ",
    " was ",
    " were ",
    " has ",
    " have ",
    " must ",
    " receive ",
    " receives ",
    " should ",
    " support ",
    " supports ",
    " allow ",
    " allows ",
    " can ",
    " cannot ",
    " will ",
    " within ",
    " after ",
    " before ",
    " percent",
    "%",
)


def extract_claims(answer: str) -> list[ExtractedClaim]:
    sentences = _split_sentences(answer)
    claims: list[ExtractedClaim] = []

    for sentence in sentences:
        cleaned = _clean_sentence(sentence)
        if not cleaned or _is_filler(cleaned):
            continue
        if not _looks_factual(cleaned):
            continue

        claims.append(ExtractedClaim(id=f"claim-{len(claims) + 1}", text=cleaned))

    return claims


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part for part in parts if part.strip()]


def _clean_sentence(sentence: str) -> str:
    cleaned = re.sub(r"\s+", " ", sentence).strip()
    return cleaned.rstrip(".!?")


def _is_filler(sentence: str) -> bool:
    lower = sentence.lower()
    return any(pattern in lower for pattern in FILLER_PATTERNS)


def _looks_factual(sentence: str) -> bool:
    lower = f" {sentence.lower()} "
    if re.search(r"\d", sentence):
        return True
    return any(hint in lower for hint in FACTUAL_HINTS)
