import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Row {
  month: string;
  income: string;
  expense: string;
}

export default function TrendChart({ data }: { data: Row[] }) {
  const chartData = data.map((d) => ({
    month: d.month,
    Income: Number(d.income),
    Expense: Number(d.expense),
  }));
  return (
    <div className="card">
      <h2>Monthly income vs. expense</h2>
      {chartData.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>No data yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip formatter={(v: number) => `₹${v.toLocaleString("en-IN")}`} />
            <Legend />
            <Bar dataKey="Income" fill="#34d399" />
            <Bar dataKey="Expense" fill="#f87171" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
