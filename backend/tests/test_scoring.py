from app.scoring import calculate_local_scores
from app.schemas import ClaimAssessment, EvaluationRequest


def test_weighted_scores() -> None:
    payload = EvaluationRequest(
        user_question="Evaluate this answer.",
        system_prompt="Answer only from context.",
        context_text="Source context exists.",
        ai_answer="Answer with three claims.",
    )
    assessments = [
        ClaimAssessment(
            claim_id="claim-1",
            claim="Supported claim",
            status="supported",
            evidence="Source context exists.",
            explanation="Supported.",
        ),
        ClaimAssessment(
            claim_id="claim-2",
            claim="Unsupported claim",
            status="unsupported",
            evidence=None,
            explanation="Unsupported.",
        ),
        ClaimAssessment(
            claim_id="claim-3",
            claim="Contradicted claim",
            status="contradicted",
            evidence="Source context exists.",
            explanation="Contradicted.",
        ),
    ]

    scores, breakdown = calculate_local_scores(payload, assessments)

    assert scores.hallucination == 53
    assert scores.citation_support == 33 
    assert scores.reasoning == 40
    assert scores.instruction_following == 60
    risk_weights = breakdown["risk_weights"]
    assert isinstance(risk_weights, dict)
    assert risk_weights["unsupported"] == 60
