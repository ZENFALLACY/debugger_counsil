"use client";

import { FormEvent, useMemo, useState } from "react";

type EvaluationForm = {
  user_question: string;
  system_prompt: string;
  context_text: string;
  ai_answer: string;
  expected_answer: string;
};

type ClaimAssessment = {
  claim_id: string;
  claim: string;
  status: string;
  evidence: string | null;
  explanation: string;
  confidence: number;
  matched_terms: string[];
  mismatched_values: string[];
};

type ExtractedClaim = {
  id: string;
  text: string;
};

type DiagnosisReport = {
  case_summary: string;
  council_summary: string;
  scores: {
    hallucination: number;
    reasoning: number;
    citation_support: number;
    instruction_following: number;
  };
  extracted_claims: ExtractedClaim[];
  supported_claims: ClaimAssessment[];
  unsupported_claims: ClaimAssessment[];
  contradicted_claims: ClaimAssessment[];
  unverifiable_claims: ClaimAssessment[];
  likely_root_cause: string;
  confidence: string | number;
  recommended_fixes: string[];
  notes: string;
  score_breakdown: Record<string, unknown>;
};

const initialForm: EvaluationForm = {
  user_question: "What is the refund window?",
  system_prompt: "Answer only from the provided policy context. If unsure, say it is not available.",
  context_text: "Refunds are available within 7 days of purchase when the customer has a receipt.",
  ai_answer: "Customers can request a refund within 30 days of purchase.",
  expected_answer: "Customers can request a refund within 7 days of purchase with a receipt.",
};

const fields: Array<{
  name: keyof EvaluationForm;
  label: string;
  placeholder: string;
  required: boolean;
}> = [
  {
    name: "user_question",
    label: "User question",
    placeholder: "What did the user ask?",
    required: true,
  },
  {
    name: "system_prompt",
    label: "System prompt",
    placeholder: "Paste the instructions given to the AI system.",
    required: true,
  },
  {
    name: "context_text",
    label: "Context / document text",
    placeholder: "Paste the retrieved context or source document.",
    required: true,
  },
  {
    name: "ai_answer",
    label: "AI answer",
    placeholder: "Paste the answer produced by the AI system.",
    required: true,
  },
  {
    name: "expected_answer",
    label: "Expected answer",
    placeholder: "Optional reference answer.",
    required: false,
  },
];

export default function Home() {
  const [form, setForm] = useState<EvaluationForm>(initialForm);
  const [report, setReport] = useState<DiagnosisReport | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiUrl = useMemo(
    () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
    [],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/evaluations/mock-diagnosis`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...form,
          expected_answer: form.expected_answer.trim() || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = (await response.json()) as { report: DiagnosisReport };
      setReport(data.report);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Unable to create diagnosis report.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="landing">
          <div className="intro">
            <p className="eyebrow">Phase 1 MVP</p>
            <h1>AI Diagnosis Council</h1>
            <p>
              A local mockup for debugging document-grounded AI answers. Submit
              one evaluation case and preview the diagnosis report shape.
            </p>
          </div>

          <div className="dashboard-mockup" aria-label="Dashboard mockup">
            <div>
              <span>Total cases</span>
              <strong>12</strong>
            </div>
            <div>
              <span>Rule checks</span>
              <strong>12</strong>
            </div>
            <div>
              <span>Judge APIs</span>
              <strong>Off</strong>
            </div>
          </div>
        </div>

        <form className="evaluation-form" onSubmit={handleSubmit}>
          {fields.map((field) => (
            <label key={field.name} className="field">
              <span>
                {field.label}
                {!field.required ? <small>Optional</small> : null}
              </span>
              <textarea
                required={field.required}
                rows={field.name === "user_question" ? 3 : 6}
                value={form[field.name]}
                placeholder={field.placeholder}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    [field.name]: event.target.value,
                  }))
                }
              />
            </label>
          ))}

          <div className="form-actions">
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Generating..." : "Generate mock report"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setForm(initialForm);
                setReport(null);
                setError(null);
              }}
            >
              Reset demo
            </button>
          </div>

          {error ? <p className="error">Backend error: {error}</p> : null}
        </form>
      </section>

      <aside className="report-panel">
        {report ? (
          <ReportView report={report} />
        ) : (
          <div className="empty-report">
            <p className="eyebrow">Mock report</p>
            <h2>Waiting for an evaluation case</h2>
            <p>
              The backend will return deterministic scores, extracted claims,
              root cause notes, and recommended fixes from local rules.
            </p>
          </div>
        )}
      </aside>
    </main>
  );
}

function ReportView({ report }: { report: DiagnosisReport }) {
  return (
    <div className="report">
      <p className="eyebrow">Diagnosis report</p>
      <h2>{report.case_summary}</h2>
      <p>{report.council_summary}</p>

      <div className="score-grid">
        {Object.entries(report.scores).map(([label, score]) => (
          <div key={label} className="score-card">
            <span>{label.replaceAll("_", " ")}</span>
            <strong>{score}</strong>
          </div>
        ))}
      </div>

      <section>
        <h3>Extracted claims</h3>
        {report.extracted_claims.length > 0 ? (
          report.extracted_claims.map((claim) => (
            <div key={claim.id} className="claim-row">
              <span>{claim.id}</span>
              <p>{claim.text}</p>
            </div>
          ))
        ) : (
          <p>No factual claims were extracted from the AI answer.</p>
        )}
      </section>

      <section>
        <h3>Supported claims</h3>
        <ClaimList
          claims={report.supported_claims}
          emptyText="No supported claims."
        />
      </section>

      <section>
        <h3>Unsupported or unverified claims</h3>
        <ClaimList
          claims={report.unsupported_claims}
          emptyText="No unsupported claims."
        />
      </section>

      <section>
        <h3>Contradicted claims</h3>
        <ClaimList
          claims={report.contradicted_claims}
          emptyText="No contradicted claims."
        />
      </section>

      <section>
        <h3>Unverifiable claims</h3>
        <ClaimList
          claims={report.unverifiable_claims}
          emptyText="No unverifiable claims."
        />
      </section>

      <section>
        <h3>Likely root cause</h3>
        <p>{report.likely_root_cause}</p>
      </section>

      <section>
        <h3>Recommended fixes</h3>
        <ul>
          {report.recommended_fixes.map((fix) => (
            <li key={fix}>{fix}</li>
          ))}
        </ul>
      </section>

      <p className="note">
        Confidence: {report.confidence}. {report.notes}
      </p>

      <section>
        <h3>Score breakdown</h3>
        <pre className="score-breakdown">
          {JSON.stringify(report.score_breakdown, null, 2)}
        </pre>
      </section>
    </div>
  );
}

function ClaimList({
  claims,
  emptyText,
}: {
  claims: ClaimAssessment[];
  emptyText: string;
}) {
  if (claims.length === 0) {
    return <p>{emptyText}</p>;
  }

  return claims.map((claim) => <ClaimRow key={claim.claim_id} claim={claim} />);
}

function ClaimRow({ claim }: { claim: ClaimAssessment }) {
  return (
    <div className="claim-row">
      <span>{claim.status}</span>
      <p>{claim.claim}</p>
      <small>{claim.evidence ?? "No evidence snippet found."}</small>
      <small>{claim.explanation}</small>
      <small>Confidence: {claim.confidence}</small>
      {claim.matched_terms.length > 0 ? (
        <small>Matched terms: {claim.matched_terms.join(", ")}</small>
      ) : null}
      {claim.mismatched_values.length > 0 ? (
        <small>Mismatched values: {claim.mismatched_values.join(", ")}</small>
      ) : null}
    </div>
  );
}
