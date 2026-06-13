import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

interface Row {
  category: string;
  total: string;
  count: number;
}

const COLORS = ["#38bdf8", "#34d399", "#fbbf24", "#f87171", "#a78bfa", "#fb923c", "#22d3ee", "#94a3b8"];

export default function CategoryChart({ data }: { data: Row[] }) {
  const chartData = data.map((d) => ({ name: d.category, value: Number(d.total) }));
  return (
    <div className="card">
      <h2>Spending by category</h2>
      {chartData.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>No expenses yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={90} label>
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(v: number) => `₹${v.toLocaleString("en-IN")}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
