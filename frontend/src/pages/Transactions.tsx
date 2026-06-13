import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Txn {
  id: number;
  date: string;
  amount: string;
  direction: string;
  merchant: string;
  description: string;
  account_last4: string;
  category: number | null;
  category_name: string | null;
}

interface Category {
  id: number;
  name: string;
}

const fmt = (v: string) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(v));

export default function Transactions() {
  const [txns, setTxns] = useState<Txn[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [direction, setDirection] = useState("");
  const [category, setCategory] = useState("");
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    const params = new URLSearchParams();
    if (direction) params.set("direction", direction);
    if (category) params.set("category", category);
    api
      .get(`/transactions/?${params.toString()}`)
      .then((r) => {
        setTxns(r.data.results);
        setCount(r.data.count);
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    api.get("/categories/").then((r) => setCategories(r.data.results ?? r.data));
  }, []);

  useEffect(load, [direction, category]);

  async function changeCategory(id: number, newCategory: string) {
    await api.patch(`/transactions/${id}/`, { category: newCategory ? Number(newCategory) : null });
    load();
  }

  return (
    <>
      <h1 style={{ fontSize: 22 }}>Transactions <span className="pill">{count}</span></h1>
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={direction} onChange={(e) => setDirection(e.target.value)}>
          <option value="">All directions</option>
          <option value="debit">Debit</option>
          <option value="credit">Credit</option>
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      <div className="card">
        {loading ? (
          <p>Loading…</p>
        ) : txns.length === 0 ? (
          <p style={{ color: "var(--muted)" }}>No transactions match these filters.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Merchant</th>
                <th>A/c</th>
                <th>Category</th>
                <th style={{ textAlign: "right" }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {txns.map((t) => (
                <tr key={t.id}>
                  <td>{t.date}</td>
                  <td>{t.merchant || <span style={{ color: "var(--muted)" }}>—</span>}</td>
                  <td>{t.account_last4 ? `••${t.account_last4}` : "—"}</td>
                  <td>
                    <select
                      value={t.category ?? ""}
                      onChange={(e) => changeCategory(t.id, e.target.value)}
                    >
                      <option value="">Uncategorized</option>
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </td>
                  <td
                    style={{ textAlign: "right" }}
                    className={t.direction === "credit" ? "badge-credit" : "badge-debit"}
                  >
                    {t.direction === "credit" ? "+" : "−"}{fmt(t.amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
