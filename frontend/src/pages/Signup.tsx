import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";
import { useAuth } from "../auth/AuthContext";

export default function Signup() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register(email, password);
      navigate("/");
    } catch (err) {
      const data = (err as AxiosError<Record<string, string[]>>).response?.data;
      const first = data && Object.values(data)[0];
      setError(Array.isArray(first) ? first[0] : "Could not create account.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-wrap">
      <h1 style={{ color: "var(--accent)" }}>EnCash</h1>
      <p style={{ color: "var(--muted)" }}>Create your account</p>
      {error && <div className="error">{error}</div>}
      <form onSubmit={onSubmit}>
        <div className="field">
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className="field">
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <small style={{ color: "var(--muted)" }}>At least 10 characters.</small>
        </div>
        <button type="submit" disabled={busy} style={{ width: "100%" }}>
          {busy ? "Creating…" : "Create account"}
        </button>
      </form>
      <p style={{ marginTop: 16, color: "var(--muted)" }}>
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </div>
  );
}
