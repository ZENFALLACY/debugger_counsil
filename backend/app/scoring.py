from app.schemas import ClaimAssessment, EvaluationRequest, Scorecard


RISK_BY_STATUS = {
    "supported": 0,
    "unsupported": 60,
    "contradicted": 100,
    "unverifiable": 70,
}


def calculate_local_scores(
    payload: EvaluationRequest, assessments: list[ClaimAssessment]
) -> tuple[Scorecard, dict[str, object]]:
    total_claims = len(assessments)
    if total_claims == 0:
        scores = Scorecard(
            hallucination=0,
            reasoning=0,
            citation_support=0,
            instruction_following=50 if not payload.context_text.strip() else 0,
        )
        return scores, _breakdown(total_claims, assessments, 0)

    risks = [RISK_BY_STATUS.get(assessment.status, 70) for assessment in assessments]
    hallucination_score = round(sum(risks) / total_claims)
    supported_count = _count_status(assessments, "supported")
    citation_support_score = round((supported_count / total_claims) * 100)

    scores = Scorecard(
        hallucination=hallucination_score,
        reasoning=_reasoning_score(assessments),
        citation_support=citation_support_score,
        instruction_following=_instruction_following_score(payload, assessments),
    )
    return scores, _breakdown(total_claims, assessments, hallucination_score)


def _reasoning_score(assessments: list[ClaimAssessment]) -> int:
    if any(assessment.status == "contradicted" for assessment in assessments):
        return 40
    if any(assessment.status in {"unsupported", "unverifiable"} for assessment in assessments):
        return 70
    return 100


def _instruction_following_score(
    payload: EvaluationRequest, assessments: list[ClaimAssessment]
) -> int:
    if not payload.context_text.strip():
        return 50

    prompt = payload.system_prompt.lower()
    risky_claim_exists = any(
        assessment.status in {"unsupported", "contradicted", "unverifiable"}
        for assessment in assessments
    )
    if "answer only from" in prompt and "context" in prompt and risky_claim_exists:
        return 60
    if all(assessment.status == "supported" for assessment in assessments):
        return 95
    return 80


def _breakdown(
    total_claims: int, assessments: list[ClaimAssessment], hallucination_score: int
) -> dict[str, object]:
    return {
        "total_claims": total_claims,
        "supported": _count_status(assessments, "supported"),
        "unsupported": _count_status(assessments, "unsupported"),
        "contradicted": _count_status(assessments, "contradicted"),
        "unverifiable": _count_status(assessments, "unverifiable"),
        "risk_weights": RISK_BY_STATUS,
        "hallucination_formula": "average claim risk",
        "hallucination_score": hallucination_score,
    }


def _count_status(assessments: list[ClaimAssessment], status: str) -> int:
    return sum(1 for assessment in assessments if assessment.status == status)
