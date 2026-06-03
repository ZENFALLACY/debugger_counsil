# AI Diagnosis Council

An AI evaluation platform that acts like a council of expert reviewers for AI-generated responses.

AI Diagnosis Council helps developers understand what failed in an AI response, why it failed, and what should be improved. The current MVP accepts an evaluation case, extracts simple factual claims, checks them against supplied context, and can optionally call an OpenAI judge for a structured diagnosis report.

## Project Vision

AI systems are becoming part of search, support, education, healthcare workflows, internal tools, and developer products. When these systems produce weak, unsupported, or misleading answers, teams often know that something went wrong but not why it happened.

AI Diagnosis Council is designed to turn AI failures into structured diagnosis reports. Instead of only showing a score, the product aims to provide a council-style review across evidence support, reasoning quality, prompt quality, and recommended fixes.

The long-term vision is an AI quality engineering platform for debugging, evaluating, benchmarking, and improving AI-generated responses.

## Problem Statement

Most AI evaluation workflows answer a narrow question: did the model output pass or fail?

That is not enough for teams building real AI products. Developers also need to know:

- Which claims are supported by the provided context?
- Which claims are unsupported, contradicted, or unverifiable?
- Did the model ignore the system prompt?
- Was the problem caused by retrieval, prompt design, reasoning, or missing context?
- What should change before the system is shipped?

The current MVP focuses on the first product surface: submitting a single AI response and receiving a structured local diagnosis report.

## Why AI Diagnosis Council Exists

AI products fail in ways that are hard to debug. A response can sound fluent while being unsupported, partially correct, or misaligned with the original instructions.

AI Diagnosis Council exists to make those failures easier to inspect. The product is positioned as a council of expert reviewers for AI-generated responses, where each future judge can evaluate a different dimension of quality:

- Evidence support
- Reasoning quality
- Prompt adherence
- Retrieval quality
- Citation quality
- Root-cause diagnosis
- Recommended fixes

The current implementation establishes the app structure, evaluation form, backend contract, claim extraction, rule-checking foundation, and a first OpenAI judge integration.

## Phase 1 Goals

Phase 1 is intentionally focused and lightweight.

Included:

- Next.js + TypeScript frontend
- FastAPI Python backend
- Evaluation submission form
- Mock diagnosis council report
- Local full-stack development setup
- Sample request and response JSON
- Project documentation suitable for GitHub, hackathons, mentor reviews, and investor discussions

Not included:

- Authentication
- Persistence or database storage
- OpenAI API integration
- Gemini API integration
- Judge APIs
- Production deployment

## Phase 2 Goals

Phase 2 adds the first deterministic backend intelligence layer.

Included:

- Simple claim extraction from AI answers
- Basic rule checker for context support
- Supported, unsupported, and contradicted claim labels
- Evidence snippets when a matching context sentence is found
- Number/date mismatch detection for obvious contradictions
- Backend tests for claim and rule behavior

Still not included:

- OpenAI API integration
- Gemini API integration
- Authentication
- Persistence
- Embeddings or vector search

## Phase 3 Goals

Phase 3 adds the first external judge integration while keeping the rest of the system simple.

Included:

- OpenAI judge endpoint
- Strict JSON response parsing
- Aggregator that combines deterministic rule checks with OpenAI judge output
- Clear error when `OPENAI_API_KEY` is missing
- Mocked tests for OpenAI judge behavior

Still not included:

- Gemini integration
- Authentication
- Persistence
- Embeddings
- Production monitoring

## Architecture Overview

```text
User
|
v
Next.js Frontend
|
v
FastAPI Backend
|
v
Claim Extractor + Rule Checker
|
v
OpenAI Judge + Aggregator
|
v
Council Report
```

The frontend collects an evaluation case from the user. The backend validates the request, extracts simple factual claims from the AI answer, checks them against the provided context, and can either return a local deterministic report or combine those rule results with an OpenAI judge response.

## Folder Structure

```text
frontend/   Next.js TypeScript frontend
backend/    FastAPI Python backend
docs/       Project notes and Phase 1 requirements
examples/   Sample request and response payloads
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend will run at `http://localhost:8000`.

Health check:

```bash
curl http://localhost:8000/health
```

Run backend tests:

```bash
cd backend
.venv\Scripts\activate
pytest
```

### OpenAI API Key

The mock endpoint does not require an API key. The OpenAI diagnosis endpoint requires `OPENAI_API_KEY`.

Create `backend/.env` or set the variable in your shell:

```bash
OPENAI_API_KEY=your_api_key_here
```

PowerShell example:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Optional model override:

```bash
OPENAI_MODEL=gpt-4.1-mini
```

Do not commit real API keys. Keep secrets in local environment variables only.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at `http://localhost:3000`.

If your backend uses a different URL, create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Demo Instructions

1. Start the backend.
2. Start the frontend.
3. Open `http://localhost:3000`.
4. Submit the sample refund-policy case from `examples/sample-request.json`.
5. Review the mock diagnosis council report in the dashboard panel.

The mock report is deterministic local data based on simple Python claim extraction and rule checks. The OpenAI endpoint uses the same local checks first, then sends the evaluation case to OpenAI for a strict JSON judge response.

## API Documentation

### Health Check

```text
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Create Local Diagnosis Report

```text
POST /api/evaluations/mock-diagnosis
```

Example request:

```json
{
  "user_question": "What is the refund window?",
  "system_prompt": "Answer only from the provided policy context. If unsure, say it is not available.",
  "context_text": "Refunds are available within 7 days of purchase when the customer has a receipt.",
  "ai_answer": "Customers can request a refund within 30 days of purchase.",
  "expected_answer": "Customers can request a refund within 7 days of purchase with a receipt."
}
```

Sample files:

- `examples/sample-request.json`
- `examples/sample-response.json`

### Create OpenAI Diagnosis Report

```text
POST /api/evaluations/openai-diagnosis
```

This endpoint requires `OPENAI_API_KEY`.

It sends the following inputs to the OpenAI judge:

- user question
- system prompt
- context
- AI answer
- extracted claims
- rule-checker results

Example request:

```json
{
  "user_question": "What is the refund window?",
  "system_prompt": "Answer only from the provided policy context. If unsure, say it is not available.",
  "context_text": "Refunds are available within 7 days of purchase when the customer has a receipt.",
  "ai_answer": "Customers can request a refund within 30 days of purchase.",
  "expected_answer": "Customers can request a refund within 7 days of purchase with a receipt."
}
```

Example response shape:

```json
{
  "report": {
    "case_summary": "Extracted 1 factual claim(s), checked them with deterministic rules, and reviewed the case with OpenAI judge.",
    "council_summary": "Phase 3 council: local claim/rule checks are combined with one OpenAI judge response. Gemini and other judges are not enabled yet.",
    "scores": {
      "hallucination": 95,
      "reasoning": 70,
      "citation_support": 5,
      "instruction_following": 80
    },
    "extracted_claims": [],
    "supported_claims": [],
    "unsupported_claims": [],
    "contradicted_claims": [],
    "likely_root_cause": "The answer used a conflicting refund window.",
    "confidence": 92,
    "recommended_fixes": ["Use the refund window from the context."],
    "notes": "Expected answer was provided. Rule checker summary: 0 supported, 0 unsupported, 1 contradicted."
  }
}
```

If `OPENAI_API_KEY` is missing, the endpoint returns a clear error instead of attempting a request.

## Mock Report Structure

The report is designed to resemble the future council output while remaining deterministic in the local MVP.

```json
{
  "report": {
    "case_summary": "Mock diagnosis for a document-grounded AI answer.",
    "council_summary": "Phase 2 local council output.",
    "scores": {
      "hallucination": 42,
      "reasoning": 74,
      "citation_support": 58,
      "instruction_following": 81
    },
    "extracted_claims": [],
    "supported_claims": [],
    "unsupported_claims": [],
    "contradicted_claims": [],
    "likely_root_cause": "Evidence verification is not implemented yet.",
    "confidence": "mock",
    "recommended_fixes": [],
    "notes": "Expected answer was provided."
  }
}
```

Report fields:

- `case_summary`: short overview of the submitted evaluation case
- `council_summary`: mock council-style interpretation of the review
- `scores`: placeholder quality scores for future evaluation dimensions
- `extracted_claims`: simple factual claims split from the AI answer
- `supported_claims`: placeholder list of claims considered supported
- `unsupported_claims`: placeholder list of claims needing review
- `contradicted_claims`: claims with obvious number/date mismatches against context
- `likely_root_cause`: mock explanation of the likely issue
- `confidence`: currently set to `mock`
- `recommended_fixes`: placeholder improvement suggestions
- `notes`: additional context about the submitted case

## OpenAI Judge JSON Contract

The OpenAI judge is instructed to return strict JSON only:

```json
{
  "hallucination_score": 0,
  "reasoning_score": 0,
  "citation_support_score": 0,
  "instruction_following_score": 0,
  "likely_root_cause": "string",
  "recommended_fixes": ["string"],
  "confidence": 0
}
```

The backend parses and validates this response before aggregation. Invalid JSON is handled safely and returned as an API error.

## Tech Stack

- Frontend: Next.js, React, TypeScript
- Backend: FastAPI, Python, Pydantic
- AI judge: OpenAI Python SDK
- Tests: pytest
- Development: local frontend and backend servers
- Data: deterministic local logic and mock JSON only

## Future Roadmap

### Phase 1

- Mock diagnosis system
- Local full-stack MVP

### Phase 2

- Claim extraction
- Basic rule checker
- Deterministic supported, unsupported, and contradicted labels

### Phase 3

- OpenAI integration
- Judge-based evaluation
- Strict JSON aggregation

### Phase 4

- Gemini integration
- Evaluation history
- Authentication
- Persistence

### Phase 5

- Multi-agent diagnosis council
- Benchmarking system
- Enterprise analytics

## Screenshots

Screenshots will be added after the Phase 1 UI is finalized.

```text
Placeholder: landing page screenshot
Placeholder: evaluation form screenshot
Placeholder: mock council report screenshot
```

## Contributing

This project is in early MVP development. Contributions should stay aligned with the current scope:

- Keep the app runnable locally.
- Use deterministic local logic only.
- Do not add external AI APIs yet.
- Do not add authentication or persistence yet.
- Prefer small, focused changes that improve the MVP foundation.

Suggested contribution areas:

- UI polish for the evaluation form and report panel
- Better sample cases in `examples/`
- Documentation improvements
- Backend response contract cleanup
- Phase 2 test coverage

## License

This repository is currently prepared as an early-stage MVP. Add a formal license before public production use or external contribution.
