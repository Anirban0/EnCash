interface Row {
  merchant: string;
  total: string;
  count: number;
}

const fmt = (v: string) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(Number(v));

export default function TopMerchants({ data }: { data: Row[] }) {
  return (
    <div className="card">
      <h2>Top merchants</h2>
      {data.length === 0 ? (
        <p style={{ color: "var(--muted)" }}>No merchants yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Merchant</th>
              <th>Txns</th>
              <th style={{ textAlign: "right" }}>Total</th>
            </tr>
          </thead>
          <tbody>
            {data.map((r) => (
              <tr key={r.merchant}>
                <td>{r.merchant}</td>
                <td>{r.count}</td>
                <td style={{ textAlign: "right" }}>{fmt(r.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
