import re

from app.normalization import extract_numbers, normalize_text
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
    "up",
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
            status="unverifiable",
            evidence=None,
            explanation="No context was provided, so the claim is unverifiable.",
            confidence=100,
        )

    claim_tokens = _keywords(claim.text)
    best_sentence, matched_terms = _find_best_evidence(context_sentences, claim_tokens)

    if not best_sentence or not matched_terms:
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="unsupported",
            evidence=None,
            explanation="No meaningful normalized term match was found in the context.",
            confidence=85,
        )

    mismatched_values = _mismatched_values(claim.text, best_sentence)
    if mismatched_values:
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="contradicted",
            evidence=best_sentence,
            explanation=(
                "The claim matches the context topic, but normalized numbers or dates "
                "conflict with the closest evidence sentence."
            ),
            confidence=_confidence(claim_tokens, matched_terms, base=82),
            matched_terms=matched_terms,
            mismatched_values=mismatched_values,
        )

    coverage = len(matched_terms) / max(len(claim_tokens), 1)
    if _normalized_contains(claim.text, best_sentence) or coverage >= 0.5:
        return ClaimAssessment(
            claim_id=claim.id,
            claim=claim.text,
            status="supported",
            evidence=best_sentence,
            explanation="The claim is supported by a normalized match in the context.",
            confidence=_confidence(claim_tokens, matched_terms, base=75),
            matched_terms=matched_terms,
        )

    return ClaimAssessment(
        claim_id=claim.id,
        claim=claim.text,
        status="unsupported",
        evidence=best_sentence,
        explanation=(
            "Related context was found, but there is not enough normalized overlap "
            "to mark the claim as supported."
        ),
        confidence=_confidence(claim_tokens, matched_terms, base=55),
        matched_terms=matched_terms,
    )


def _find_best_evidence(
    context_sentences: list[str], claim_tokens: set[str]
) -> tuple[str, list[str]]:
    best_sentence = ""
    best_terms: list[str] = []

    for sentence in context_sentences:
        sentence_tokens = _keywords(sentence)
        matched_terms = sorted(claim_tokens.intersection(sentence_tokens))
        if len(matched_terms) > len(best_terms):
            best_sentence = sentence
            best_terms = matched_terms

    return best_sentence, best_terms


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip().rstrip(".!?") for part in parts if part.strip()]


def _keywords(text: str) -> set[str]:
    words = normalize_text(text).split()
    return {
        word
        for word in words
        if word not in STOP_WORDS and (len(word) > 1 or word.isdigit())
    }


def _normalized_contains(claim_text: str, evidence_text: str) -> bool:
    return normalize_text(claim_text) in normalize_text(evidence_text)


def _mismatched_values(claim_text: str, evidence_text: str) -> list[str]:
    claim_values = set(extract_numbers(claim_text))
    evidence_values = set(extract_numbers(evidence_text))
    if not claim_values or not evidence_values:
        return []
    if not _keywords(claim_text).intersection(_keywords(evidence_text)):
        return []
    if claim_values.intersection(evidence_values):
        return []
    return sorted(claim_values.union(evidence_values))


def _confidence(claim_tokens: set[str], matched_terms: list[str], base: int) -> int:
    coverage = len(matched_terms) / max(len(claim_tokens), 1)
    return min(100, round(base + (coverage * 25)))
