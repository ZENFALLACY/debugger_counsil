from app.main import create_mock_diagnosis
from app.schemas import EvaluationRequest


def test_endpoint_marks_matching_refund_claim_supported() -> None:
    payload = EvaluationRequest(
        user_question="What is the refund window?",
        system_prompt="Answer only from the provided policy context.",
        context_text=(
            "Refunds are available within 7 days of purchase when the customer "
            "has a receipt."
        ),
        ai_answer="Customers can request a refund within 7 days of purchase.",
        expected_answer=(
            "Customers can request a refund within 7 days of purchase with a receipt."
        ),
    )

    response = create_mock_diagnosis(payload)
    report = response.report

    assert report.scores.hallucination == 0
    assert report.scores.citation_support == 100
    assert len(report.supported_claims) == 1
    assert len(report.unsupported_claims) == 0
    assert len(report.contradicted_claims) == 0
