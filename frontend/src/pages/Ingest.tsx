import { FormEvent, useState } from "react";
import { api } from "../api/client";

interface Summary {
  inserted: number;
  duplicates: number;
  unparsed: string[];
}

const SAMPLE = `Rs.1,200.00 debited from A/c XX1234 on 12-Jun-26 at AMAZON. Avl Bal Rs.5,000.00
INR 500 credited to A/c no. XX5678 on 01-06-2026. Avl Bal INR 10,000
Rs 250.00 spent on Card xx9999 at SWIGGY on 10-06-26
Rs.2000 withdrawn from A/c XX1234 at ATM on 03-06-2026`;

export default function Ingest() {
  const [raw, setRaw] = useState("");
  const [result, setResult] = useState<Summary | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const { data } = await api.post("/ingest/sms/", { raw });
      setResult(data);
    } catch {
      setError("Could not import. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1 style={{ fontSize: 22 }}>Import SMS alerts</h1>
      <p style={{ color: "var(--muted)" }}>
        Paste your bank transaction SMS alerts below, one per line.
      </p>
      <form onSubmit={onSubmit}>
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          placeholder="Rs.1,200.00 debited from A/c XX1234 on 12-Jun-26 at AMAZON…"
        />
        <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
          <button type="submit" disabled={busy || !raw.trim()}>
            {busy ? "Importing…" : "Import"}
          </button>
          <button
            type="button"
            onClick={() => setRaw(SAMPLE)}
            style={{ background: "var(--surface-2)", color: "var(--text)" }}
          >
            Load sample
          </button>
        </div>
      </form>

      {error && <div className="error" style={{ marginTop: 16 }}>{error}</div>}

      {result && (
        <div className="card" style={{ marginTop: 20 }}>
          <h2>Import result</h2>
          <p>
            <strong className="badge-credit">{result.inserted}</strong> imported,{" "}
            <strong>{result.duplicates}</strong> duplicates skipped,{" "}
            <strong>{result.unparsed.length}</strong> could not be parsed.
          </p>
          {result.unparsed.length > 0 && (
            <>
              <h2>Unparsed messages</h2>
              <ul style={{ color: "var(--muted)" }}>
                {result.unparsed.map((u, i) => (
                  <li key={i}><code>{u}</code></li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </>
  );
}
