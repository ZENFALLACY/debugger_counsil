from app.schemas import (
    ClaimAssessment,
    DiagnosisReport,
    EvaluationRequest,
    ExtractedClaim,
    OpenAIJudgeResult,
    Scorecard,
)
from app.scoring import calculate_local_scores


def aggregate_openai_report(
    payload: EvaluationRequest,
    extracted_claims: list[ExtractedClaim],
    rule_checker_results: list[ClaimAssessment],
    judge_result: OpenAIJudgeResult,
) -> DiagnosisReport:
    supported_claims = [
        assessment for assessment in rule_checker_results if assessment.status == "supported"
    ]
    unsupported_claims = [
        assessment
        for assessment in rule_checker_results
        if assessment.status == "unsupported"
    ]
    contradicted_claims = [
        assessment
        for assessment in rule_checker_results
        if assessment.status == "contradicted"
    ]
    unverifiable_claims = [
        assessment
        for assessment in rule_checker_results
        if assessment.status == "unverifiable"
    ]
    _, score_breakdown = calculate_local_scores(payload, rule_checker_results)

    return DiagnosisReport(
        case_summary=(
            f"Extracted {len(extracted_claims)} factual claim(s), checked them "
            "with deterministic rules, and reviewed the case with OpenAI judge."
        ),
        council_summary=(
            "Phase 3 council: local claim/rule checks are combined with one OpenAI "
            "judge response. Gemini and other judges are not enabled yet."
        ),
        scores=Scorecard(
            hallucination=judge_result.hallucination_score,
            reasoning=judge_result.reasoning_score,
            citation_support=judge_result.citation_support_score,
            instruction_following=judge_result.instruction_following_score,
        ),
        extracted_claims=extracted_claims,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        contradicted_claims=contradicted_claims,
        unverifiable_claims=unverifiable_claims,
        likely_root_cause=judge_result.likely_root_cause,
        confidence=judge_result.confidence,
        recommended_fixes=judge_result.recommended_fixes,
        notes=_notes(payload, supported_claims, unsupported_claims, contradicted_claims),
        score_breakdown=score_breakdown,
    )


def _notes(
    payload: EvaluationRequest,
    supported_claims: list[ClaimAssessment],
    unsupported_claims: list[ClaimAssessment],
    contradicted_claims: list[ClaimAssessment],
) -> str:
    expected_note = (
        "Expected answer was provided."
        if payload.expected_answer
        else "No expected answer was provided."
    )
    return (
        f"{expected_note} Rule checker summary: {len(supported_claims)} supported, "
        f"{len(unsupported_claims)} unsupported, {len(contradicted_claims)} contradicted."
    )
