from app.aggregator import aggregate_openai_report
from app.rules import check_claims_against_context
from app.schemas import EvaluationRequest, ExtractedClaim, OpenAIJudgeResult


def test_aggregator_combines_rules_and_openai_judge() -> None:
    payload = EvaluationRequest(
        user_question="What is the refund window?",
        system_prompt="Answer only from context.",
        context_text="Refunds are available within 7 days of purchase.",
        ai_answer="Refunds are available within 30 days of purchase.",
    )
    claims = [
        ExtractedClaim(id="claim-1", text="Refunds are available within 30 days")
    ]
    assessments = check_claims_against_context(payload.context_text, claims)
    judge_result = OpenAIJudgeResult(
        hallucination_score=95,
        reasoning_score=70,
        citation_support_score=5,
        instruction_following_score=80,
        likely_root_cause="The answer used a conflicting refund window.",
        recommended_fixes=["Use the refund window from the context."],
        confidence=92,
    )

    report = aggregate_openai_report(payload, claims, assessments, judge_result)

    assert report.scores.hallucination == 95
    assert report.confidence == 92
    assert len(report.contradicted_claims) == 1
    assert report.recommended_fixes == ["Use the refund window from the context."]
