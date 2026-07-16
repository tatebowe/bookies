import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ClubDashboard, createCycle, decideJoinRequest, getClubDashboard, getDashboard, getJoinRequests, getSuggestions, JoinRequest, Suggestion, updateClubSettings, updateCycle, updateMemberRole } from "../lib/api";

export function ClubPage() {
  const { clubId } = useParams();
  const navigate = useNavigate();
  const [club, setClub] = useState<ClubDashboard | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [error, setError] = useState("");
  const [dashboardRole, setDashboardRole] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("tomeys_token");
    if (!token || !clubId) { navigate("/auth", { replace: true }); return; }
    Promise.all([getClubDashboard(clubId, token), getSuggestions(clubId, token)])
      .then(([clubDashboard, clubSuggestions]) => { setClub(clubDashboard); setSuggestions(clubSuggestions); })
      .catch((requestError: Error) => setError(requestError.message));
  }, [clubId, navigate]);

  useEffect(() => {
    const token = localStorage.getItem("tomeys_token");
    if (!token || !clubId) return;
    getDashboard(token).then((dashboard) => setDashboardRole(dashboard.clubs.find((membership) => String(membership.club.id) === clubId)?.role ?? "")).catch(() => undefined);
  }, [clubId]);

  if (error) return <main className="map-page"><section className="auth-content"><h1>This chapter is closed.</h1><p>{error}</p><Link className="text-link" to="/dashboard">Return to dashboard</Link></section></main>;
  if (!club) return <main className="map-page"><p className="loading-ink">Opening the club ledger…</p></main>;
  const total = Object.values(club.reading_progress).reduce((sum, value) => sum + value, 0) || 1;
  const readingPercent = (club.reading_progress.reading / total) * 100;
  const completedPercent = (club.reading_progress.completed / total) * 100;
  const cycleLabel = club.active_cycle ? club.active_cycle.phase.replaceAll("_", " ") : "between reading cycles";
  const viewerRole = club.viewer_role || dashboardRole;
  const reloadClub = () => { const token = localStorage.getItem("tomeys_token"); if (token && clubId) Promise.all([getClubDashboard(clubId, token), getSuggestions(clubId, token)]).then(([nextClub, nextSuggestions]) => { setClub(nextClub); setSuggestions(nextSuggestions); }); };

  return <main className="dashboard-page club-page">
    <header className="dashboard-header"><Link className="brand" to="/dashboard">Tomeys</Link><Link className="back-link" to="/dashboard">← All clubs</Link></header>
    <section className="club-hero"><p className="eyebrow">Club ledger</p><h1>{club.club.name}</h1><p>{club.club.description || "A shared shelf for good books and better conversation."}</p><span className="cycle-label">{cycleLabel}</span></section>
    <section className="club-layout">
      <article className="dashboard-card feature-book">
        <p className="eyebrow">Current selection</p>
        {club.current_book ? <><div className="large-book-spine" /><h2>{club.current_book.title}</h2><p>{club.current_book.authors || "Author unknown"}</p>{club.active_cycle?.discussion_date && <p className="date-note">Discussion: {new Date(club.active_cycle.discussion_date).toLocaleDateString()}</p>}</> : <><EmptyState text="A new read will be selected when the next cycle begins." /><Link className="quiet-link" to={`/books?clubId=${clubId}`}>Suggest a book →</Link></>}
      </article>
      <article className="dashboard-card progress-card"><p className="eyebrow">Reading progress</p><div className="progress-summary"><strong>{club.reading_progress.completed}</strong><span>members finished</span></div><div className="progress-bar"><span className="progress-reading" style={{ width: `${readingPercent}%` }} /><span className="progress-completed" style={{ width: `${completedPercent}%` }} /></div><div className="progress-key"><span>Not started · {club.reading_progress.not_started}</span><span>Reading · {club.reading_progress.reading}</span><span>Finished · {club.reading_progress.completed}</span></div><p className="discussion-count">{club.discussion_notes_count} discussion notes shared</p></article>
      <article className="dashboard-card suggestions-card"><div className="card-heading"><p className="eyebrow">Book suggestions</p><span>{suggestions.length} in the running</span></div>{suggestions.length ? suggestions.map((suggestion) => <div className="suggestion-row" key={suggestion.id}><div className="suggestion-book">{suggestion.book.title.charAt(0)}</div><div><h2>{suggestion.book.title}</h2><p>{suggestion.book.authors || "Author unknown"}</p></div><span className="vote-count">{suggestion.vote_count} vote{suggestion.vote_count === 1 ? "" : "s"}</span></div>) : <EmptyState text="There are no suggestions yet. The next great read is yours to propose." />}</article>
      <article className="dashboard-card members-card"><div className="card-heading"><p className="eyebrow">Members</p><span>{club.members.length} readers</span></div><div className="member-list">{club.members.map((member) => <div className="member-row" key={member.username}><span>{member.username.charAt(0).toUpperCase()}</span><p>{member.username}<small>{member.role}</small></p></div>)}</div></article>
    </section>
    {(viewerRole === "owner" || viewerRole === "admin") && <ControlDrawer club={club} role={viewerRole} clubId={clubId!} onSaved={reloadClub} />}
  </main>;
}

function EmptyState({ text }: { text: string }) { return <p className="empty-state">{text}</p>; }

function ControlDrawer({ club, role, clubId, onSaved }: { club: ClubDashboard; role: string; clubId: string; onSaved: () => void }) {
  const [open, setOpen] = useState(false); const [requests, setRequests] = useState<JoinRequest[]>([]); const [message, setMessage] = useState(""); const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("tomeys_token");
  useEffect(() => { if (open && token) getJoinRequests(clubId, token).then(setRequests).catch((err: Error) => setMessage(err.message)); }, [clubId, open, token]);
  async function decide(request: JoinRequest, approved: boolean) { if (!token) return; setBusy(true); try { await decideJoinRequest(request.id, approved, token); setRequests((current) => current.filter((item) => item.id !== request.id)); setMessage(approved ? "Join request approved." : "Join request rejected."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not process request."); } finally { setBusy(false); } }
  async function promote(username: string) { if (!token) return; setBusy(true); try { await updateMemberRole(clubId, username, "admin", token); setMessage(`${username} is now an admin.`); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not update role."); } finally { setBusy(false); } }
  async function saveCycle(event: React.FormEvent<HTMLFormElement>, future: boolean) { event.preventDefault(); if (!token) return; const data = new FormData(event.currentTarget); const values = { name: String(data.get("name") || ""), suggestion_start_date: new Date(String(data.get("suggestion"))).toISOString(), voting_start_date: new Date(String(data.get("voting"))).toISOString(), voting_end_date: new Date(String(data.get("voteEnd"))).toISOString(), discussion_date: new Date(String(data.get("discussion"))).toISOString() }; setBusy(true); try { if (future) await createCycle(clubId, values, token); else if (club.active_cycle) await updateCycle(club.active_cycle.id, values, token); setMessage(future ? "Future cycle scheduled." : "Current cycle updated."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not save cycle."); } finally { setBusy(false); } }
  const cycleFields = (_prefix: string, defaults?: ClubDashboard["active_cycle"]) => <><input name="name" defaultValue={defaults?.id ? `Cycle ${defaults.id}` : ""} placeholder="Cycle name (optional)" /><label>Suggestions start<input required type="datetime-local" name="suggestion" defaultValue={defaults?.suggestion_start_date ? new Date(defaults.suggestion_start_date).toISOString().slice(0, 16) : ""} /></label><label>Voting starts<input required type="datetime-local" name="voting" defaultValue={defaults?.voting_start_date ? new Date(defaults.voting_start_date).toISOString().slice(0, 16) : ""} /></label><label>Voting ends<input required type="datetime-local" name="voteEnd" defaultValue={defaults?.voting_end_date ? new Date(defaults.voting_end_date).toISOString().slice(0, 16) : ""} /></label><label>Discussion date<input required type="datetime-local" name="discussion" defaultValue={defaults?.discussion_date ? new Date(defaults.discussion_date).toISOString().slice(0, 16) : ""} /></label></>;
  return <><button className="club-controls-trigger" onClick={() => setOpen(true)}>Club controls</button>{open && <div className="control-overlay" role="dialog" aria-modal="true" aria-label="Club controls"><button className="control-scrim" aria-label="Close controls" onClick={() => setOpen(false)} /><aside className="control-drawer"><button className="drawer-close" onClick={() => setOpen(false)}>×</button><p className="eyebrow">{role} controls</p><h2>Club controls</h2><section><h3>Join requests</h3>{requests.length ? requests.map((request) => <div className="request-row" key={request.id}><span>Reader #{request.user_id}</span><button disabled={busy} onClick={() => decide(request, true)}>Accept</button><button disabled={busy} onClick={() => decide(request, false)}>Reject</button></div>) : <p>No pending requests.</p>}</section>{club.active_cycle && <form className="manage-form" onSubmit={(event) => saveCycle(event, false)}><h3>Edit current cycle</h3>{cycleFields("current", club.active_cycle)}<button disabled={busy}>Save cycle</button></form>}<form className="manage-form" onSubmit={(event) => saveCycle(event, true)}><h3>Schedule a future cycle</h3>{cycleFields("future")}<button disabled={busy}>Schedule cycle</button></form><ManagementPanel club={{ ...club, viewer_role: role }} clubId={clubId} onSaved={onSaved} />{message && <p className="reading-message">{message}</p>}</aside></div>}</>;
}

function ManagementPanel({ club, clubId, onSaved }: { club: ClubDashboard; clubId: string; onSaved: () => void }) {
  const [message, setMessage] = useState(""); const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("tomeys_token"); const owner = club.viewer_role === "owner";
  async function startCycle(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (!token) return; const data = new FormData(event.currentTarget); setBusy(true); try { await createCycle(clubId, { name: String(data.get("name") || ""), suggestion_start_date: new Date(String(data.get("suggestion"))).toISOString(), voting_start_date: new Date(String(data.get("voting"))).toISOString(), voting_end_date: new Date(String(data.get("voteEnd"))).toISOString(), discussion_date: new Date(String(data.get("discussion"))).toISOString() }, token); setMessage("New cycle started."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not start cycle."); } finally { setBusy(false); } }
  async function saveSettings(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (!token) return; const data = new FormData(event.currentTarget); setBusy(true); try { await updateClubSettings(clubId, { is_public: data.get("visibility") === "public", join_policy: String(data.get("policy")), max_votes_per_user: Number(data.get("votes")) }, token); setMessage("Club settings saved."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not save settings."); } finally { setBusy(false); } }
  async function promote(username: string) { if (!token) return; setBusy(true); try { await updateMemberRole(clubId, username, "admin", token); setMessage(`${username} is now an admin.`); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not update role."); } finally { setBusy(false); } }
  return <section className="management-panel"><p className="eyebrow">{owner ? "Owner controls" : "Admin controls"}</p><h2>Manage this club</h2>{!club.active_cycle && <form className="manage-form cycle-form" onSubmit={startCycle}><h3>Start the next cycle</h3><input name="name" placeholder="Cycle name (optional)" /><label>Suggestions start<input required type="datetime-local" name="suggestion" /></label><label>Voting starts<input required type="datetime-local" name="voting" /></label><label>Voting ends<input required type="datetime-local" name="voteEnd" /></label><label>Discussion date<input required type="datetime-local" name="discussion" /></label><button disabled={busy}>Start cycle</button></form>}{owner && <><form className="manage-form" onSubmit={saveSettings}><h3>Club settings</h3><label>Visibility<select name="visibility" defaultValue={club.club.is_public ? "public" : "private"}><option value="public">Public</option><option value="private">Private</option></select></label><label>Joining<select name="policy" defaultValue={club.club.join_policy}><option value="open">Open — join instantly</option><option value="request">Request approval</option></select></label><label>Votes per member<input name="votes" type="number" min="1" defaultValue={club.club.max_votes_per_user} /></label><button disabled={busy}>Save settings</button></form><div className="manage-form"><h3>Promote members</h3>{club.members.filter((member) => member.role === "member").map((member) => <div className="promote-row" key={member.username}><span>{member.username}</span><button disabled={busy} onClick={() => promote(member.username)}>Make admin</button></div>)}</div></>}{message && <p className="reading-message">{message}</p>}</section>;
}
