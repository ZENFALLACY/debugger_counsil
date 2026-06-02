# AI Diagnosis Council

An AI evaluation platform that acts like a council of expert reviewers for AI-generated responses.

AI Diagnosis Council helps developers understand what failed in an AI response, why it failed, and what should be improved. The current MVP accepts an evaluation case, extracts simple factual claims, checks them against supplied context, and returns a deterministic diagnosis council report without calling any external AI APIs.

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

The current implementation does not use real LLM judges yet. It establishes the app structure, evaluation form, backend contract, claim extraction, and rule-checking foundation.

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
Council Report
```

The frontend collects an evaluation case from the user. The backend validates the request, extracts simple factual claims from the AI answer, checks them against the provided context, and returns deterministic report data shaped like a future AI Diagnosis Council evaluation.

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

The report is deterministic local data based on simple Python claim extraction and rule checks. External judge integrations are intentionally disabled.

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

## Tech Stack

- Frontend: Next.js, React, TypeScript
- Backend: FastAPI, Python, Pydantic
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
- Gemini integration
- Judge-based evaluation

### Phase 4

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
