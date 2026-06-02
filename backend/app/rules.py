import re

from app.schemas import ClaimAssessment, ExtractedClaim


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
    "within",
}


def check_claims_against_context(
    context: str, claims: list[ExtractedClaim]
) -> list[ClaimAssessment]:
    context_sentences = _split_sentences(context)

    return [_assess_claim(context_sentences, claim) for claim in claims]


def _assess_claim(
    context_sentences: list[str], claim: ExtractedClaim
) -> ClaimAssessment:
    if not context_sentences:
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="unsupported",
            evidence=None,
            explanation="No context was provided, so the claim cannot be verified.",
        )

    claim_tokens = _keywords(claim.text)
    best_sentence = ""
    best_score = 0

    for sentence in context_sentences:
        sentence_tokens = _keywords(sentence)
        score = len(claim_tokens.intersection(sentence_tokens))
        if score > best_score:
            best_sentence = sentence
            best_score = score

    if not best_sentence or best_score == 0:
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="unsupported",
            evidence=None,
            explanation="No meaningful keyword match was found in the context.",
        )

    if _has_number_or_date_mismatch(claim.text, best_sentence):
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="contradicted",
            evidence=best_sentence,
            explanation=(
                "The claim overlaps with the context, but a number or date differs "
                "from the closest evidence sentence."
            ),
        )

    coverage = best_score / max(len(claim_tokens), 1)
    if _normalized(claim.text) in _normalized(best_sentence) or coverage >= 0.55:
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="supported",
            evidence=best_sentence,
            explanation="The claim has strong keyword overlap with the context.",
        )

    return ClaimAssessment(
        claim_id=claim.id,
        claim=claim.text,
        status="unsupported",
        evidence=best_sentence,
        explanation=(
            "Some related context was found, but there is not enough overlap to "
            "mark the claim as supported."
        ),
    )


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip().rstrip(".!?") for part in parts if part.strip()]


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {
        _normalize_word(word)
        for word in words
        if word not in STOP_WORDS and len(word) > 1
    }


def _normalize_word(word: str) -> str:
    if word.endswith("ies") and len(word) > 4:
        return f"{word[:-3]}y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _normalized(text: str) -> str:
    return " ".join(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def _has_number_or_date_mismatch(claim_text: str, evidence_text: str) -> bool:
    claim_values = set(_extract_numbers_and_dates(claim_text))
    evidence_values = set(_extract_numbers_and_dates(evidence_text))
    if not claim_values or not evidence_values:
        return False

    shared_subject = _keywords(claim_text).intersection(_keywords(evidence_text))
    return bool(shared_subject) and claim_values.isdisjoint(evidence_values)


def _extract_numbers_and_dates(text: str) -> list[str]:
    values = re.findall(r"\b\d{1,4}(?:[-/]\d{1,2}(?:[-/]\d{1,4})?)?\b", text)
    month_dates = re.findall(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b",
        text.lower(),
    )
    return values + month_dates
