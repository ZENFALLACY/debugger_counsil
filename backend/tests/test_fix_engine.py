from app.fix_engine import generate_fix_recommendations
from app.schemas import ClaimAssessment


def test_contradicted_number_fix() -> None:
    assessment = ClaimAssessment(
        claim_id="claim-1",
        claim="Refunds are available within 30 days of purchase",
        status="contradicted",
        evidence="Refunds are available within 7 days of purchase",
        explanation="Numbers conflict.",
        confidence=99,
        mismatched_values=["30", "7"],
    )

    result = generate_fix_recommendations([assessment])
    fixed_claim = result.assessments[0]

    assert fixed_claim.root_cause == (
        "The claim conflicts with the evidence because 30, 7 do not match."
    )
    assert "Replace the contradicted wording" in fixed_claim.fix_suggestion
    assert fixed_claim.corrected_claim == "Refunds are available within 7 days of purchase"


def test_unsupported_claim_fix() -> None:
    assessment = ClaimAssessment(
        claim_id="claim-1",
        claim="The plan includes phone support",
        status="unsupported",
        evidence=None,
        explanation="No meaningful normalized term match was found in the context.",
        confidence=85,
    )

    result = generate_fix_recommendations([assessment])
    fixed_claim = result.assessments[0]

    assert fixed_claim.root_cause == (
        "No evidence sentence in the supplied context supports this claim."
    )
    assert fixed_claim.fix_suggestion == (
        "Remove this claim, or add source evidence that directly supports it."
    )
    assert fixed_claim.corrected_claim == ""


def test_unverifiable_claim_fix() -> None:
    assessment = ClaimAssessment(
        claim_id="claim-1",
        claim="The plan includes a service-level agreement",
        status="unverifiable",
        evidence=None,
        explanation="No context was provided, so the claim is unverifiable.",
        confidence=100,
    )

    result = generate_fix_recommendations([assessment])
    fixed_claim = result.assessments[0]

    assert fixed_claim.root_cause == "There is no usable context evidence for this claim."
    assert "Verify the claim with additional sources" in fixed_claim.fix_suggestion
    assert fixed_claim.corrected_claim == ""


def test_supported_claim_no_fix() -> None:
    assessment = ClaimAssessment(
        claim_id="claim-1",
        claim="Refunds are available within 7 days of purchase",
        status="supported",
        evidence="Refunds are available within 7 days of purchase",
        explanation="The claim is supported by a normalized match in the context.",
        confidence=95,
    )

    result = generate_fix_recommendations([assessment])
    fixed_claim = result.assessments[0]

    assert fixed_claim.root_cause == "The claim is supported by the available evidence."
    assert fixed_claim.fix_suggestion == "No fix needed."
    assert fixed_claim.corrected_claim == assessment.claim


def test_corrected_answer_generation() -> None:
    supported = ClaimAssessment(
        claim_id="claim-1",
        claim="The Pro plan supports 10 users",
        status="supported",
        evidence="The Pro plan supports 10 users",
        explanation="Supported.",
        confidence=95,
    )
    contradicted = ClaimAssessment(
        claim_id="claim-2",
        claim="Refunds are available within 30 days",
        status="contradicted",
        evidence="Refunds are available within 7 days",
        explanation="Contradicted.",
        confidence=99,
        mismatched_values=["30", "7"],
    )
    unsupported = ClaimAssessment(
        claim_id="claim-3",
        claim="The plan includes phone support",
        status="unsupported",
        evidence=None,
        explanation="Unsupported.",
        confidence=85,
    )

    result = generate_fix_recommendations([supported, contradicted, unsupported])

    assert result.corrected_answer_draft == (
        "The Pro plan supports 10 users. Refunds are available within 7 days."
    )
    assert "Remove unsupported claims" in result.overall_fix_recommendations[1]
