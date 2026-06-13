interface Summary {
  income: string;
  expense: string;
  net: string;
  count: number;
}

const fmt = (v: string) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(v));

export default function SummaryCards({ summary }: { summary: Summary }) {
  return (
    <div className="cards-grid">
      <div className="card stat">
        <div className="label">Income</div>
        <div className="value green">{fmt(summary.income)}</div>
      </div>
      <div className="card stat">
        <div className="label">Expense</div>
        <div className="value red">{fmt(summary.expense)}</div>
      </div>
      <div className="card stat">
        <div className="label">Net</div>
        <div className={`value ${Number(summary.net) >= 0 ? "green" : "red"}`}>
          {fmt(summary.net)}
        </div>
      </div>
      <div className="card stat">
        <div className="label">Transactions</div>
        <div className="value">{summary.count}</div>
      </div>
    </div>
  );
}
