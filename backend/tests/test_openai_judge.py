import pytest

from app.judges.openai_judge import (
    OpenAIJudgeConfigError,
    OpenAIJudgeResponseError,
    parse_openai_judge_json,
    run_openai_judge,
)
from app.rules import check_claims_against_context
from app.schemas import EvaluationRequest, ExtractedClaim


VALID_JUDGE_JSON = """
{
  "hallucination_score": 10,
  "reasoning_score": 88,
  "citation_support_score": 91,
  "instruction_following_score": 84,
  "likely_root_cause": "The answer is mostly supported, with minor wording risk.",
  "recommended_fixes": ["Add direct citations."],
  "confidence": 87
}
"""


def test_parse_openai_judge_json() -> None:
    result = parse_openai_judge_json(VALID_JUDGE_JSON)

    assert result.hallucination_score == 10
    assert result.confidence == 87
    assert result.recommended_fixes == ["Add direct citations."]


def test_parse_openai_judge_invalid_json() -> None:
    with pytest.raises(OpenAIJudgeResponseError):
        parse_openai_judge_json("not json")


def test_run_openai_judge_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(OpenAIJudgeConfigError):
        run_openai_judge(_payload(), [], [])


def test_run_openai_judge_uses_mocked_openai_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        output_text = VALID_JUDGE_JSON

    class FakeResponses:
        def create(self, **kwargs: object) -> FakeResponse:
            captured.update(kwargs)
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key: str) -> None:
            captured["api_key"] = api_key
            self.responses = FakeResponses()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("app.judges.openai_judge.OpenAI", FakeClient)

    payload = _payload()
    claims = [ExtractedClaim(id="claim-1", text="Refunds are available within 7 days")]
    assessments = check_claims_against_context(payload.context_text, claims)
    result = run_openai_judge(payload, claims, assessments)

    assert result.reasoning_score == 88
    assert captured["api_key"] == "test-key"
    assert captured["model"] == "gpt-4.1-mini"
    text_config = captured["text"]
    assert isinstance(text_config, dict)
    assert text_config["format"]["type"] == "json_schema"
    assert text_config["format"]["strict"] is True


def _payload() -> EvaluationRequest:
    return EvaluationRequest(
        user_question="What is the refund window?",
        system_prompt="Answer only from context.",
        context_text="Refunds are available within 7 days of purchase.",
        ai_answer="Refunds are available within 7 days of purchase.",
        expected_answer=None,
    )
