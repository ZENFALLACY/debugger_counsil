from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    user_question: str = Field(..., min_length=1)
    system_prompt: str = Field(..., min_length=1)
    context_text: str = Field(..., min_length=1)
    ai_answer: str = Field(..., min_length=1)
    expected_answer: str | None = None


class ExtractedClaim(BaseModel):
    id: str
    text: str


class ClaimAssessment(BaseModel):
    claim_id: str
    claim: str
    status: str
    evidence: str | None = None
    explanation: str


class Scorecard(BaseModel):
    hallucination: int
    reasoning: int
    citation_support: int
    instruction_following: int


class DiagnosisReport(BaseModel):
    case_summary: str
    council_summary: str
    scores: Scorecard
    extracted_claims: list[ExtractedClaim]
    supported_claims: list[ClaimAssessment]
    unsupported_claims: list[ClaimAssessment]
    contradicted_claims: list[ClaimAssessment]
    likely_root_cause: str
    confidence: str
    recommended_fixes: list[str]
    notes: str


class EvaluationResponse(BaseModel):
    report: DiagnosisReport
