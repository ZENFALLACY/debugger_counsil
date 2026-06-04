import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.judges.prompts import OPENAI_JUDGE_SYSTEM_PROMPT, build_openai_judge_prompt
from app.schemas import (
    ClaimAssessment,
    EvaluationRequest,
    ExtractedClaim,
    OpenAIJudgeResult,
)


load_dotenv()


class OpenAIJudgeConfigError(RuntimeError):
    pass


class OpenAIJudgeResponseError(RuntimeError):
    pass


OPENAI_JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "hallucination_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "reasoning_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "citation_support_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "instruction_following_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
        "likely_root_cause": {"type": "string"},
        "recommended_fixes": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
    },
    "required": [
        "hallucination_score",
        "reasoning_score",
        "citation_support_score",
        "instruction_following_score",
        "likely_root_cause",
        "recommended_fixes",
        "confidence",
    ],
}


def run_openai_judge(
    payload: EvaluationRequest,
    extracted_claims: list[ExtractedClaim],
    rule_checker_results: list[ClaimAssessment],
) -> OpenAIJudgeResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIJudgeConfigError(
            "OPENAI_API_KEY is missing. Set it in your environment before using OpenAI diagnosis."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)
    prompt = build_openai_judge_prompt(payload, extracted_claims, rule_checker_results)

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": OPENAI_JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ai_diagnosis_council_openai_judge",
                    "strict": True,
                    "schema": OPENAI_JUDGE_SCHEMA,
                }
            },
            timeout=30.0,
        )
    except OpenAIError as exc:
        raise OpenAIJudgeResponseError(f"OpenAI request failed: {exc}") from exc

    return parse_openai_judge_json(response.output_text)


def parse_openai_judge_json(raw_json: str) -> OpenAIJudgeResult:
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise OpenAIJudgeResponseError("OpenAI judge returned invalid JSON.") from exc

    try:
        return OpenAIJudgeResult.model_validate(parsed)
    except ValidationError as exc:
        raise OpenAIJudgeResponseError(
            "OpenAI judge JSON did not match the expected schema."
        ) from exc
