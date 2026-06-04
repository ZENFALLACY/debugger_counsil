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
    confidence: int = Field(default=0, ge=0, le=100)
    matched_terms: list[str] = Field(default_factory=list)
    mismatched_values: list[str] = Field(default_factory=list)
    root_cause: str = ""
    fix_suggestion: str = ""
    corrected_claim: str = ""


class Scorecard(BaseModel):
    hallucination: int
    reasoning: int
    citation_support: int
    instruction_following: int


class OpenAIJudgeResult(BaseModel):
    hallucination_score: int = Field(..., ge=0, le=100)
    reasoning_score: int = Field(..., ge=0, le=100)
    citation_support_score: int = Field(..., ge=0, le=100)
    instruction_following_score: int = Field(..., ge=0, le=100)
    likely_root_cause: str
    recommended_fixes: list[str]
    confidence: int = Field(..., ge=0, le=100)


class DiagnosisReport(BaseModel):
    case_summary: str
    council_summary: str
    scores: Scorecard
    extracted_claims: list[ExtractedClaim]
    supported_claims: list[ClaimAssessment]
    unsupported_claims: list[ClaimAssessment]
    contradicted_claims: list[ClaimAssessment]
    unverifiable_claims: list[ClaimAssessment] = Field(default_factory=list)
    likely_root_cause: str
    overall_root_cause: str = ""
    confidence: int | str
    recommended_fixes: list[str]
    overall_fix_recommendations: list[str] = Field(default_factory=list)
    corrected_answer_draft: str = ""
    notes: str
    score_breakdown: dict[str, object] = Field(default_factory=dict)


class EvaluationResponse(BaseModel):
    report: DiagnosisReport
