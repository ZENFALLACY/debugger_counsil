from dataclasses import dataclass

from app.schemas import ClaimAssessment


@dataclass(frozen=True)
class FixEngineResult:
    assessments: list[ClaimAssessment]
    overall_root_cause: str
    overall_fix_recommendations: list[str]
    corrected_answer_draft: str


def generate_fix_recommendations(
    assessments: list[ClaimAssessment],
) -> FixEngineResult:
    enriched_assessments = [_enrich_assessment(assessment) for assessment in assessments]

    return FixEngineResult(
        assessments=enriched_assessments,
        overall_root_cause=_overall_root_cause(enriched_assessments),
        overall_fix_recommendations=_overall_fix_recommendations(enriched_assessments),
        corrected_answer_draft=_corrected_answer_draft(enriched_assessments),
    )


def _enrich_assessment(assessment: ClaimAssessment) -> ClaimAssessment:
    if assessment.status == "supported":
        return assessment.model_copy(
            update={
                "root_cause": "The claim is supported by the available evidence.",
                "fix_suggestion": "No fix needed.",
                "corrected_claim": assessment.claim,
            }
        )

    if assessment.status == "unsupported":
        evidence_note = (
            f"The closest evidence is: {assessment.evidence}."
            if assessment.evidence
            else "No evidence sentence in the supplied context supports this claim."
        )
        return assessment.model_copy(
            update={
                "root_cause": evidence_note,
                "fix_suggestion": (
                    "Remove this claim, or add source evidence that directly supports it."
                ),
                "corrected_claim": "",
            }
        )

    if assessment.status == "contradicted":
        mismatches = (
            ", ".join(assessment.mismatched_values)
            if assessment.mismatched_values
            else "the claim and evidence values"
        )
        corrected_claim = assessment.evidence or ""
        return assessment.model_copy(
            update={
                "root_cause": (
                    "The claim conflicts with the evidence because "
                    f"{mismatches} do not match."
                ),
                "fix_suggestion": (
                    "Replace the contradicted wording with the closest evidence-backed wording."
                ),
                "corrected_claim": corrected_claim,
            }
        )

    if assessment.status == "unverifiable":
        return assessment.model_copy(
            update={
                "root_cause": "There is no usable context evidence for this claim.",
                "fix_suggestion": (
                    "Verify the claim with additional sources before keeping it in the answer."
                ),
                "corrected_claim": "",
            }
        )

    return assessment.model_copy(
        update={
            "root_cause": "The claim status is not recognized by the fix engine.",
            "fix_suggestion": "Review this claim manually.",
            "corrected_claim": "",
        }
    )


def _overall_root_cause(assessments: list[ClaimAssessment]) -> str:
    counts = _status_counts(assessments)
    if counts["contradicted"]:
        return (
            "The answer includes claims that conflict with the supplied evidence, "
            "usually because a value or date was copied incorrectly."
        )
    if counts["unsupported"]:
        return (
            "The answer includes claims that are not backed by the supplied context."
        )
    if counts["unverifiable"]:
        return "The answer cannot be fully verified because evidence context is missing."
    return "All extracted claims are supported by the supplied evidence."


def _overall_fix_recommendations(assessments: list[ClaimAssessment]) -> list[str]:
    counts = _status_counts(assessments)
    recommendations: list[str] = []

    if counts["contradicted"]:
        recommendations.append(
            "Replace contradicted values or wording with the evidence-backed version."
        )
    if counts["unsupported"]:
        recommendations.append(
            "Remove unsupported claims or add source evidence before keeping them."
        )
    if counts["unverifiable"]:
        recommendations.append(
            "Add retrieval context or external sources for unverifiable claims."
        )
    if not recommendations:
        recommendations.append("No repair needed for the extracted claims.")

    return recommendations


def _corrected_answer_draft(assessments: list[ClaimAssessment]) -> str:
    corrected_claims = [
        assessment.corrected_claim.strip()
        for assessment in assessments
        if assessment.corrected_claim.strip()
    ]
    if corrected_claims:
        return _join_sentences(corrected_claims)
    return "No corrected answer draft can be generated without supported evidence."


def _join_sentences(claims: list[str]) -> str:
    sentences = []
    for claim in claims:
        sentence = claim.rstrip(".!?")
        sentences.append(f"{sentence}.")
    return " ".join(sentences)


def _status_counts(assessments: list[ClaimAssessment]) -> dict[str, int]:
    return {
        "supported": sum(
            1 for assessment in assessments if assessment.status == "supported"
        ),
        "unsupported": sum(
            1 for assessment in assessments if assessment.status == "unsupported"
        ),
        "contradicted": sum(
            1 for assessment in assessments if assessment.status == "contradicted"
        ),
        "unverifiable": sum(
            1 for assessment in assessments if assessment.status == "unverifiable"
        ),
    }
