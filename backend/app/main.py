from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.claims import extract_claims
from app.rules import check_claims_against_context
from app.schemas import (
    DiagnosisReport,
    EvaluationRequest,
    EvaluationResponse,
    Scorecard,
)


app = FastAPI(title="AI Diagnosis Council API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/evaluations/mock-diagnosis", response_model=EvaluationResponse)
def create_mock_diagnosis(payload: EvaluationRequest) -> EvaluationResponse:
    claims = extract_claims(payload.ai_answer)
    assessments = check_claims_against_context(payload.context_text, claims)
    supported_claims = [
        assessment for assessment in assessments if assessment.status == "supported"
    ]
    unsupported_claims = [
        assessment for assessment in assessments if assessment.status == "unsupported"
    ]
    contradicted_claims = [
        assessment for assessment in assessments if assessment.status == "contradicted"
    ]

    expected_note = (
        "Expected answer was provided, so a future judge can compare against it."
        if payload.expected_answer
        else "No expected answer was provided, so this mock report focuses on context support."
    )
    total_claims = len(claims)
    supported_count = len(supported_claims)
    contradicted_count = len(contradicted_claims)
    unsupported_count = len(unsupported_claims)

    report = DiagnosisReport(
        case_summary=(
            f"Extracted {total_claims} factual claim(s) from the AI answer and "
            "checked them against the supplied context."
        ),
        council_summary=(
            "Phase 2 local council: deterministic claim extraction and rule checks "
            "are active. External AI judges are still disabled."
        ),
        scores=Scorecard(
            hallucination=_hallucination_score(total_claims, unsupported_count, contradicted_count),
            reasoning=74,
            citation_support=_support_score(total_claims, supported_count),
            instruction_following=81,
        ),
        extracted_claims=claims,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        contradicted_claims=contradicted_claims,
        likely_root_cause=(
            _root_cause(unsupported_count, contradicted_count)
        ),
        confidence="mock",
        recommended_fixes=[
            "Add a context-only instruction to the system prompt.",
            "Require citations or short evidence snippets for factual claims.",
            "Review unsupported and contradicted claims before enabling external judge APIs.",
        ],
        notes=expected_note,
    )

    return EvaluationResponse(report=report)


def _support_score(total_claims: int, supported_count: int) -> int:
    if total_claims == 0:
        return 0
    return round((supported_count / total_claims) * 100)


def _hallucination_score(
    total_claims: int, unsupported_count: int, contradicted_count: int
) -> int:
    if total_claims == 0:
        return 0
    risky_claims = unsupported_count + contradicted_count
    return round((risky_claims / total_claims) * 100)


def _root_cause(unsupported_count: int, contradicted_count: int) -> str:
    if contradicted_count:
        return (
            "At least one claim appears contradicted by the context, likely due to "
            "the answer using a conflicting fact."
        )
    if unsupported_count:
        return (
            "At least one claim could not be verified from the context, likely due "
            "to missing evidence or an answer that goes beyond the source text."
        )
    return "All extracted claims were supported by the supplied context."
