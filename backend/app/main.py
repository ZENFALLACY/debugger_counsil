from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    user_question: str = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=1)
    context_text: str = Field(..., min_length=1)
    ai_answer: str = Field(..., min_length=1)
    expected_answer: str | None = None


class Scorecard(BaseModel):
    hallucination: int
    reasoning: int
    citation_support: int
    instruction_following: int


class ClaimAssessment(BaseModel):
    claim: str
    status: str
    evidence: str


class DiagnosisReport(BaseModel):
    case_summary: str
    council_summary: str
    scores: Scorecard
    supported_claims: list[ClaimAssessment]
    unsupported_claims: list[ClaimAssessment]
    likely_root_cause: str
    confidence: str
    recommended_fixes: list[str]
    notes: str


class EvaluationResponse(BaseModel):
    report: DiagnosisReport


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
    expected_note = (
        "Expected answer was provided, so a future judge can compare against it."
        if payload.expected_answer
        else "No expected answer was provided, so this mock report focuses on context support."
    )

    report = DiagnosisReport(
        case_summary=(
            "Mock diagnosis for a document-grounded AI answer. The app received the "
            "question, prompt, context, and model answer successfully."
        ),
        council_summary=(
            "Phase 1 mock council: evidence, reasoning, prompt, and fix judges are "
            "represented as placeholder output only."
        ),
        scores=Scorecard(
            hallucination=42,
            reasoning=74,
            citation_support=58,
            instruction_following=81,
        ),
        supported_claims=[
            ClaimAssessment(
                claim="The answer attempts to respond to the submitted user question.",
                status="supported",
                evidence="Request fields were present and non-empty.",
            )
        ],
        unsupported_claims=[
            ClaimAssessment(
                claim="Some answer details may not be grounded in the supplied context.",
                status="needs_review",
                evidence="Phase 1 uses a mock report and does not run claim extraction yet.",
            )
        ],
        likely_root_cause=(
            "Evidence verification is not implemented yet. The next phase should add "
            "rule checks and model judges before treating scores as real."
        ),
        confidence="mock",
        recommended_fixes=[
            "Add a context-only instruction to the system prompt.",
            "Require citations or short evidence snippets for factual claims.",
            "Add rule-based support checks before enabling external judge APIs.",
        ],
        notes=expected_note,
    )

    return EvaluationResponse(report=report)
