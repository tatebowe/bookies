import { Link, useNavigate } from "react-router-dom";

export function AppHeader({ greeting }: { greeting?: string }) {
  const navigate = useNavigate();
  function signOut() {
    localStorage.removeItem("tomeys_token");
    navigate("/");
  }

  return <header className="dashboard-header"><Link className="brand" to="/dashboard">Tomeys</Link><nav className="header-actions" aria-label="Main navigation">{greeting && <span>{greeting}</span>}<Link className="header-link" to="/clubs">Clubs</Link><Link className="header-link" to="/books">Books</Link><Link className="header-link" to="/profile">Profile</Link><button className="sign-out" type="button" onClick={signOut}>Sign out</button></nav></header>;
}
