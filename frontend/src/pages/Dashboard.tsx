import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import SummaryCards from "../components/SummaryCards";
import CategoryChart from "../components/CategoryChart";
import TrendChart from "../components/TrendChart";
import TopMerchants from "../components/TopMerchants";

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [byCategory, setByCategory] = useState<any[]>([]);
  const [trend, setTrend] = useState<any[]>([]);
  const [merchants, setMerchants] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/analytics/summary/"),
      api.get("/analytics/by-category/"),
      api.get("/analytics/trend/"),
      api.get("/analytics/top-merchants/"),
    ])
      .then(([s, c, t, m]) => {
        setSummary(s.data);
        setByCategory(c.data);
        setTrend(t.data);
        setMerchants(m.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading…</p>;

  if (summary && summary.count === 0) {
    return (
      <div className="card">
        <h2>Welcome to EnCash</h2>
        <p style={{ color: "var(--muted)" }}>
          You have no transactions yet. Import your bank SMS alerts to get started.
        </p>
        <Link to="/ingest"><button>Import SMS alerts</button></Link>
      </div>
    );
  }

  return (
    <>
      {summary && <SummaryCards summary={summary} />}
      <div className="chart-grid">
        <CategoryChart data={byCategory} />
        <TrendChart data={trend} />
      </div>
      <TopMerchants data={merchants} />
    </>
  );
}
