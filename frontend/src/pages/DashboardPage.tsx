import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Dashboard, getDashboard, saveReadingNote, saveReadingReview, updateReadingStatus } from "../lib/api";

export function DashboardPage() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  const refreshDashboard = () => {
    const token = localStorage.getItem("tomeys_token");
    if (token) getDashboard(token).then(setDashboard).catch((requestError: Error) => setError(requestError.message));
  };

  useEffect(() => {
    const token = localStorage.getItem("tomeys_token");
    if (!token) { navigate("/auth", { replace: true }); return; }
    getDashboard(token).then(setDashboard).catch((requestError: Error) => { localStorage.removeItem("tomeys_token"); setError(requestError.message); });
  }, [navigate]);

  if (error) return <main className="map-page"><section className="auth-content"><h1>Let’s try that again.</h1><p>{error}</p><Link className="text-link" to="/auth">Return to sign in</Link></section></main>;
  if (!dashboard) return <main className="map-page"><p className="loading-ink">Gathering your reading life…</p></main>;
  const name = dashboard.profile.display_name || dashboard.profile.username;
  const signOut = () => { localStorage.removeItem("tomeys_token"); navigate("/"); };

  return <main className="dashboard-page">
    <header className="dashboard-header"><Link className="brand" to="/dashboard">Tomeys</Link><div className="header-actions"><span>Welcome, {name}</span><button className="sign-out" onClick={signOut}>Sign out</button></div></header>
    <section className="dashboard-hero"><p className="eyebrow">Your reading room</p><h1>Good to see you, {name}.</h1><p>Keep your club, your current chapter, and your notes all within reach.</p></section>
    <section className="dashboard-grid">
      <article className="dashboard-card current-card"><CardHeading label="On your nightstand" count={`${dashboard.current_readings.length} active`} />{dashboard.current_readings.length ? dashboard.current_readings.map((reading) => <div className="reading-item" key={reading.id}><div className="reading-row"><div className="book-spine" /><div><h2>{reading.book.title}</h2><p>{reading.book.authors || "Author unknown"}{reading.club ? ` · ${reading.club.name}` : " · personal reading"}</p></div><span className="status-pill">{reading.status.replaceAll("_", " ")}</span></div><ReadingActions reading={reading} onSaved={refreshDashboard} /></div>) : <EmptyState text="No book in progress yet. Your club’s next pick will appear here." />}</article>
      <article className="dashboard-card clubs-card"><CardHeading label="Your clubs" count={`${dashboard.clubs.length} joined`} />{dashboard.clubs.length ? dashboard.clubs.map(({ club, role, active_cycle }) => <div className="club-row" key={club.id}><div className="club-monogram">{club.name.charAt(0)}</div><div><Link className="club-link" to={`/clubs/${club.id}`}>{club.name}</Link><p>{role}{active_cycle ? ` · ${active_cycle.phase.replaceAll("_", " ")}` : " · between reads"}</p></div></div>) : <EmptyState text="Your first book club is waiting to be discovered." />}<Link className="quiet-link" to="/clubs">Find a club →</Link></article>
      <article className="dashboard-card notes-card"><CardHeading label="Recent notes" count={`${dashboard.notes.length} saved`} />{dashboard.notes.length ? dashboard.notes.slice(0, 3).map((note) => <div className="note-row" key={note.id}><h2>{note.book?.title || "General reading note"}</h2><time dateTime={note.created_at}>{new Date(note.created_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}</time><p>{note.content}</p></div>) : <EmptyState text="A thought worth keeping? Your reading notes will collect here." />}<button className="quiet-button">Write a note</button></article>
      <article className="dashboard-card history-card"><CardHeading label="Reading history" count={`${dashboard.history.length} finished`} />{dashboard.history.length ? dashboard.history.slice(0, 3).map((entry) => <div className="history-row" key={entry.id}><span>{entry.rating ? "★".repeat(Math.round(entry.rating)) : "—"}</span><div><h2>{entry.book.title}</h2><p>{entry.club?.name || "Personal reading"}</p></div></div>) : <EmptyState text="The books you finish with your clubs will live here." />}<Link className="quiet-link" to="/books">Search books →</Link></article>
    </section>
  </main>;
}

function CardHeading({ label, count }: { label: string; count: string }) { return <div className="card-heading"><p className="eyebrow">{label}</p><span>{count}</span></div>; }
function EmptyState({ text }: { text: string }) { return <p className="empty-state">{text}</p>; }

function ReadingActions({ reading, onSaved }: { reading: Dashboard["current_readings"][number]; onSaved: () => void }) {
  const [note, setNote] = useState(""); const [review, setReview] = useState(""); const [rating, setRating] = useState("5"); const [message, setMessage] = useState(""); const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("tomeys_token");
  async function changeStatus(status: string) { if (!token) return; setBusy(true); try { await updateReadingStatus(reading.id, status, token); setMessage("Reading status updated."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not update status."); } finally { setBusy(false); } }
  async function addNote() { if (!token || !note.trim()) return; setBusy(true); try { await saveReadingNote(reading.id, note, token); setNote(""); setMessage("Note saved."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not save note."); } finally { setBusy(false); } }
  async function addReview() { if (!token || !review.trim()) return; setBusy(true); try { await saveReadingReview(reading.id, Number(rating), review, token); setReview(""); setMessage("Review saved."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not save review."); } finally { setBusy(false); } }
  return <div className="reading-actions"><div className="status-actions"><span>Update status:</span>{["not_started", "reading", "completed"].map((status) => <button disabled={busy || reading.status === status} key={status} onClick={() => changeStatus(status)}>{status.replaceAll("_", " ")}</button>)}</div><div className="reading-writing"><label>Quick note<textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="Capture a thought…" /></label><button disabled={busy || !note.trim()} onClick={addNote}>Save note</button></div>{reading.status === "completed" && <div className="reading-writing review-writing"><label>Review<textarea value={review} onChange={(event) => setReview(event.target.value)} placeholder="What stayed with you?" /></label><label>Rating<select value={rating} onChange={(event) => setRating(event.target.value)}>{[1, 2, 3, 4, 5].map((value) => <option key={value} value={value}>{value} stars</option>)}</select></label><button disabled={busy || !review.trim()} onClick={addReview}>Save review</button></div>}{message && <p className="reading-message">{message}</p>}</div>;
}
