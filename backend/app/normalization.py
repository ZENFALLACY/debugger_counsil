import re


PHRASE_REPLACEMENTS = (
    (r"\bteam members\b", "user"),
    (r"\bone week\b", "7 days"),
    (r"\bseven days\b", "7 days"),
    (r"\bthirty days\b", "30 days"),
    (r"\bfive\b", "5"),
    (r"\bten\b", "10"),
)

WORD_REPLACEMENTS = {
    "refunds": "refund",
    "customers": "customer",
    "users": "user",
    "members": "user",
    "seats": "user",
    "seat": "user",
    "licenses": "plan",
    "license": "plan",
    "subscriptions": "plan",
    "subscription": "plan",
    "allows": "allow",
    "allowed": "allow",
    "permits": "allow",
    "permitted": "allow",
    "supports": "support",
    "supported": "support",
}


def normalize_text(text: str) -> str:
    normalized = text.lower()
    for pattern, replacement in PHRASE_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized)

    words = re.findall(r"[a-zA-Z0-9]+", normalized)
    normalized_words = [_normalize_word(word) for word in words]
    return " ".join(normalized_words)


def extract_numbers(text: str) -> list[str]:
    normalized = normalize_text(text)
    values = re.findall(r"\b\d{1,4}(?:[-/]\d{1,2}(?:[-/]\d{1,4})?)?\b", normalized)
    month_dates = re.findall(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b",
        normalized,
    )
    return values + month_dates


def _normalize_word(word: str) -> str:
    if word in WORD_REPLACEMENTS:
        return WORD_REPLACEMENTS[word]
    if word.endswith("ies") and len(word) > 4:
        return f"{word[:-3]}y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word
