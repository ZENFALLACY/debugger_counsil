from app.schemas import ClaimAssessment, EvaluationRequest, ExtractedClaim


OPENAI_JUDGE_SYSTEM_PROMPT = """
You are the OpenAI judge in AI Diagnosis Council.
Evaluate whether an AI-generated answer is supported by the provided context.
Return strict JSON only. Do not include markdown, prose, comments, or code fences.
Scores must be integers from 0 to 100.
""".strip()


def build_openai_judge_prompt(
    payload: EvaluationRequest,
    extracted_claims: list[ExtractedClaim],
    rule_checker_results: list[ClaimAssessment],
) -> str:
    return f"""
Evaluate this AI answer using the provided context, extracted claims, and deterministic rule-checker results.

User question:
{payload.user_question}

System prompt:
{payload.system_prompt}

Context:
{payload.context_text}

AI answer:
{payload.ai_answer}

Extracted claims:
{[claim.model_dump() for claim in extracted_claims]}

Rule checker results:
{[result.model_dump() for result in rule_checker_results]}

Return exactly this JSON object shape:
{{
  "hallucination_score": 0,
  "reasoning_score": 0,
  "citation_support_score": 0,
  "instruction_following_score": 0,
  "likely_root_cause": "string",
  "recommended_fixes": ["string"],
  "confidence": 0
}}
""".strip()
