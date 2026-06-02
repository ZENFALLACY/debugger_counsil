from app.claims import extract_claims
from app.rules import check_claims_against_context
from app.schemas import ExtractedClaim


def test_supported_claim() -> None:
    claims = [ExtractedClaim(id="claim-1", text="Refunds are available within 7 days")]
    results = check_claims_against_context(
        "Refunds are available within 7 days of purchase.", claims
    )

    assert results[0].status == "supported"
    assert results[0].evidence == "Refunds are available within 7 days of purchase"


def test_unsupported_claim() -> None:
    claims = [ExtractedClaim(id="claim-1", text="Customers receive free shipping")]
    results = check_claims_against_context(
        "Refunds are available within 7 days of purchase.", claims
    )

    assert results[0].status == "unsupported"


def test_contradicted_refund_days_claim() -> None:
    claims = [ExtractedClaim(id="claim-1", text="Refunds are available within 30 days")]
    results = check_claims_against_context(
        "Refunds are available within 7 days of purchase.", claims
    )

    assert results[0].status == "contradicted"
    assert "7 days" in (results[0].evidence or "")


def test_empty_context() -> None:
    claims = [ExtractedClaim(id="claim-1", text="Refunds are available within 7 days")]
    results = check_claims_against_context("", claims)

    assert results[0].status == "unsupported"
    assert results[0].evidence is None


def test_multiple_claims() -> None:
    answer = (
        "Refunds are available within 7 days. "
        "Customers receive free shipping. "
        "I hope this helps."
    )

    claims = extract_claims(answer)
    results = check_claims_against_context(
        "Refunds are available within 7 days of purchase.", claims
    )

    assert [claim.id for claim in claims] == ["claim-1", "claim-2"]
    assert [result.status for result in results] == ["supported", "unsupported"]
