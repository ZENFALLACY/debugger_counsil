# Phase 1 Requirements

This summary is derived from `AI_Diagnosis_Council_Master_Plan.pdf` and scoped to the first local MVP only.

## Goal

Build a runnable local app that lets a developer submit a document-grounded AI answer and receive a mock diagnosis report.

## Inputs

- user question
- system prompt
- context or document text
- AI answer
- optional expected answer

## Output

The backend returns deterministic mock data shaped like a future AI Diagnosis Council report:

- hallucination score
- reasoning score
- citation/support score
- instruction-following score
- supported claim placeholders
- unsupported claim placeholders
- likely root cause
- recommended fixes

## Phase 1 Constraints

- Use mock data only.
- Do not call OpenAI, Gemini, or any other LLM API.
- Do not build judge APIs yet.
- Do not add database, auth, export, tracing, or production deployment.
- Make the app easy to run locally.
