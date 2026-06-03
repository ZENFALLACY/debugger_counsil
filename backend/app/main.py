from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.aggregator import aggregate_openai_report
from app.claims import extract_claims
from app.judges.openai_judge import (
    OpenAIJudgeConfigError,
    OpenAIJudgeResponseError,
    run_openai_judge,
)
from app.rules import check_claims_against_context
from app.scoring import calculate_local_scores
from app.schemas import (
    DiagnosisReport,
    EvaluationRequest,
    EvaluationResponse,
)


app = FastAPI(title="AI Diagnosis Council API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://[::1]:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://[::1]:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/evaluations/mock-diagnosis", response_model=EvaluationResponse)
def create_mock_diagnosis(payload: EvaluationRequest) -> EvaluationResponse:
    claims, assessments = _run_local_pipeline(payload)
    supported_claims = [
        assessment for assessment in assessments if assessment.status == "supported"
    ]
    unsupported_claims = [
        assessment for assessment in assessments if assessment.status == "unsupported"
    ]
    contradicted_claims = [
        assessment for assessment in assessments if assessment.status == "contradicted"
    ]
    unverifiable_claims = [
        assessment for assessment in assessments if assessment.status == "unverifiable"
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
    local_scores, score_breakdown = calculate_local_scores(payload, assessments)

    report = DiagnosisReport(
        case_summary=(
            f"Extracted {total_claims} factual claim(s) from the AI answer and "
            "checked them against the supplied context."
        ),
        council_summary=(
            "Phase 3.5 local council: normalized rule checks and explainable "
            "claim-level scoring are active. External AI judges are still optional."
        ),
        scores=local_scores,
        extracted_claims=claims,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        contradicted_claims=contradicted_claims,
        unverifiable_claims=unverifiable_claims,
        likely_root_cause=(
            _root_cause(unsupported_count, contradicted_count, len(unverifiable_claims))
        ),
        confidence="mock",
        recommended_fixes=[
            "Add a context-only instruction to the system prompt.",
            "Require citations or short evidence snippets for factual claims.",
            "Review unsupported and contradicted claims before enabling external judge APIs.",
        ],
        notes=expected_note,
        score_breakdown=score_breakdown,
    )

    return EvaluationResponse(report=report)


@app.post("/api/evaluations/openai-diagnosis", response_model=EvaluationResponse)
def create_openai_diagnosis(payload: EvaluationRequest) -> EvaluationResponse:
    claims, assessments = _run_local_pipeline(payload)

    try:
        judge_result = run_openai_judge(payload, claims, assessments)
    except OpenAIJudgeConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OpenAIJudgeResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return EvaluationResponse(
        report=aggregate_openai_report(payload, claims, assessments, judge_result)
    )


def _run_local_pipeline(
    payload: EvaluationRequest,
):
    claims = extract_claims(payload.ai_answer)
    assessments = check_claims_against_context(payload.context_text, claims)
    return claims, assessments


def _root_cause(
    unsupported_count: int, contradicted_count: int, unverifiable_count: int
) -> str:
    if contradicted_count:
        return (
            "At least one claim appears contradicted by the context, likely due to "
            "the answer using a conflicting fact."
        )
    if unverifiable_count:
        return "At least one claim is unverifiable because no evidence context was available."
    if unsupported_count:
        return (
            "At least one claim could not be verified from the context, likely due "
            "to missing evidence or an answer that goes beyond the source text."
        )
    return "All extracted claims were supported by the supplied context."
