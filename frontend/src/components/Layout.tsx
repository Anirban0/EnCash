import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Layout() {
  const { email, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <>
      <nav className="navbar">
        <span className="brand">EnCash</span>
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/transactions">Transactions</NavLink>
        <NavLink to="/ingest">Import</NavLink>
        <span className="spacer" />
        <span style={{ color: "var(--muted)", fontSize: 14 }}>{email}</span>
        <button onClick={handleLogout} style={{ padding: "6px 12px" }}>Logout</button>
      </nav>
      <main className="container">
        <Outlet />
      </main>
    </>
  );
}
