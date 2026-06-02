# Phase 1 Scope

Phase 1 implements the first local MVP slice from the AI Diagnosis Council master plan.

## Included

- Full-stack app shell
- Next.js + TypeScript frontend
- FastAPI Python backend
- Evaluation form for:
  - user question
  - system prompt
  - context/document text
  - AI answer
  - optional expected answer
- Mock diagnosis endpoint
- Demo example payload
- README setup steps

## Deferred

- OpenAI judge
- Gemini judge
- Rule checker
- Aggregator
- Claim extraction
- Database
- Authentication
- Export flows
- Production deployment

## Mock Endpoint

`POST /api/evaluations/mock-diagnosis`

The response shape is intentionally close to the future report contract, but all scores and claim assessments are deterministic placeholder values.
