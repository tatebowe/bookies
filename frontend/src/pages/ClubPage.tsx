import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { castSuggestionVote, ClubDashboard, ClubHistory, ClubInvitation, createCycle, createDiscussionNote, decideJoinRequest, DiscussionNote, getClubDashboard, getClubHistory, getClubInvitations, getCycleDiscussionNotes, getDashboard, getJoinRequests, getSuggestions, inviteMember, JoinRequest, revokeInvitation, Suggestion, updateClubSettings, updateCycle, updateMemberRole } from "../lib/api";
import { AppHeader } from "../components/AppHeader";

export function ClubPage() {
  const { clubId } = useParams();
  const navigate = useNavigate();
  const [club, setClub] = useState<ClubDashboard | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [history, setHistory] = useState<ClubHistory["history"]>([]);
  const [error, setError] = useState("");
  const [dashboardRole, setDashboardRole] = useState("");
  const [membersOpen, setMembersOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("tomeys_token");
    if (!token || !clubId) { navigate("/auth", { replace: true }); return; }
    getClubDashboard(clubId, token)
      .then((clubDashboard) => { setClub(clubDashboard); return getSuggestions(clubId, token).catch(() => []); })
      .then(setSuggestions)
      .catch((requestError: Error) => setError(requestError.message));
  }, [clubId, navigate]);

  useEffect(() => { const token = localStorage.getItem("tomeys_token"); if (token && clubId) getClubHistory(clubId, token).then((result) => setHistory(result.history)).catch(() => undefined); }, [clubId]);

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
  const viewerRole = dashboardRole || club.viewer_role;
  const reloadClub = () => { const token = localStorage.getItem("tomeys_token"); if (token && clubId) { getClubDashboard(clubId, token).then(setClub).then(() => getSuggestions(clubId, token).catch(() => [])).then(setSuggestions).catch(() => undefined); getClubHistory(clubId, token).then((result) => setHistory(result.history)).catch(() => undefined); } };

  return <main className="dashboard-page club-page">
    <AppHeader />
    <section className="club-hero"><p className="eyebrow">Club ledger</p><h1>{club.club.name}</h1><p>{club.club.description || "A shared shelf for good books and better conversation."}</p><div className="club-cycle-line"><span className="cycle-label">{club.active_cycle?.name ? `${club.active_cycle.name} · ${cycleLabel}` : cycleLabel}</span><button className="members-trigger" type="button" onClick={() => setMembersOpen(true)}>Members · {club.members.length}</button></div></section>
    <section className="club-layout">
      <article className="dashboard-card feature-book">
        <p className="eyebrow">Current selection</p>
        {club.current_book ? <><div className="large-book-spine" /><h2>{club.current_book.title}</h2><p>{club.current_book.authors || "Author unknown"}</p>{club.current_book.suggested_by_display_name && <p className="suggested-by">Suggested by {club.current_book.suggested_by_display_name}</p>}{club.active_cycle?.discussion_date && <p className="date-note">Discussion: {formatLocalDateTime(club.active_cycle.discussion_date)}</p>}{club.future_cycles.length > 0 && <div className="future-cycle-list"><p className="eyebrow">Up next</p>{club.future_cycles.map((cycle) => <p key={cycle.id}><strong>{cycle.name || "Next reading cycle"}</strong> · suggestions open {formatLocalDateTime(cycle.suggestion_start_date)}</p>)}</div>}</> : <><EmptyState text="A new read will be selected when the next cycle begins." /><Link className="quiet-link" to={`/books?clubId=${clubId}`}>Suggest a book →</Link></>}
        {club.active_cycle && !club.current_book && <div className="cycle-schedule"><p className="eyebrow">Current cycle</p><h3>{club.active_cycle.name || "Untitled cycle"}</h3><p>Suggestions open: {formatLocalDateTime(club.active_cycle.suggestion_start_date)}</p><p>Voting opens: {formatLocalDateTime(club.active_cycle.voting_start_date)}</p><p>Voting closes: {formatLocalDateTime(club.active_cycle.voting_end_date)}</p></div>}
      </article>
      <article className="dashboard-card progress-card"><p className="eyebrow">Reading progress</p><div className="progress-summary"><strong>{club.reading_progress.completed}</strong><span>members finished</span></div><div className="progress-bar"><span className="progress-reading" style={{ width: `${readingPercent}%` }} /><span className="progress-completed" style={{ width: `${completedPercent}%` }} /></div><div className="progress-key"><span>Not started · {club.reading_progress.not_started}</span><span>Reading · {club.reading_progress.reading}</span><span>Finished · {club.reading_progress.completed}</span></div>{club.active_cycle && club.viewer_club_reading_id && <DiscussionNotes cycleId={club.active_cycle.id} clubReadingId={club.viewer_club_reading_id} discussionDate={club.active_cycle.discussion_date} />}</article>
      <SuggestionsCard club={club} clubId={clubId!} suggestions={suggestions} onSubmitted={reloadClub} />
      <article className="dashboard-card cycle-history-card"><div className="card-heading"><p className="eyebrow">Past cycles</p><span>{history.length} completed</span></div>{history.length ? history.map((cycle) => <div className="past-cycle-row" key={cycle.cycle_id}><div><h2>{cycle.cycle_name || "Reading cycle"}</h2><p>Winner: <strong>{cycle.book.title}</strong></p><p>{cycle.book.authors || "Author unknown"}</p><PastCycleNotes cycleId={cycle.cycle_id} count={cycle.discussion_notes_count} /></div><time dateTime={cycle.end_date}>{formatLocalDateTime(cycle.end_date)}</time></div>) : <EmptyState text="Past winning books will collect here." />}</article>
    </section>
    {membersOpen && <div className="members-popout" role="dialog" aria-modal="true" aria-label="Club members"><button className="members-scrim" type="button" aria-label="Close members" onClick={() => setMembersOpen(false)} /><aside><button className="drawer-close" type="button" onClick={() => setMembersOpen(false)}>×</button><p className="eyebrow">Club readers</p><h2>Members</h2><div className="member-list">{club.members.map((member) => <div className="member-row" key={member.username}><span>{(member.display_name || member.username).charAt(0).toUpperCase()}</span><p>{member.display_name || member.username}<small>{member.role}</small></p></div>)}</div></aside></div>}
    {(viewerRole === "owner" || viewerRole === "admin") && <ControlDrawer club={club} role={viewerRole} clubId={clubId!} onSaved={reloadClub} />}
  </main>;
}

function EmptyState({ text }: { text: string }) { return <p className="empty-state">{text}</p>; }

function DiscussionNotes({ cycleId, clubReadingId, discussionDate }: { cycleId: number; clubReadingId: number; discussionDate: string | null }) {
  const [notes, setNotes] = useState<DiscussionNote[]>([]); const [content, setContent] = useState(""); const [message, setMessage] = useState(""); const [saving, setSaving] = useState(false);
  const refresh = () => { const token = localStorage.getItem("tomeys_token"); if (token) getCycleDiscussionNotes(cycleId, token).then(setNotes).catch((error: Error) => setMessage(error.message)); };
  useEffect(refresh, [cycleId]);
  const discussionOpen = discussionDate ? new Date(/(?:Z|[+-]\d{2}:\d{2})$/.test(discussionDate) ? discussionDate : `${discussionDate}Z`) <= new Date() : false;
  async function save() { const token = localStorage.getItem("tomeys_token"); if (!token || !content.trim()) return; setSaving(true); try { await createDiscussionNote(clubReadingId, content.trim(), token); setContent(""); setMessage(discussionOpen ? "Discussion note shared." : "Private note saved. It will be shared on the discussion date."); refresh(); } catch (error) { setMessage(error instanceof Error ? error.message : "Could not save discussion note."); } finally { setSaving(false); } }
  return <div className="discussion-notes"><p className="eyebrow">Discussion notes</p><p className="discussion-note-help">{discussionOpen ? "Club notes are now shared." : "Your notes stay private until the discussion date."}</p><textarea value={content} onChange={(event) => setContent(event.target.value)} placeholder="Capture a thought for the discussion…" /><button type="button" disabled={saving || !content.trim()} onClick={save}>{saving ? "Saving…" : "Save discussion note"}</button>{notes.length > 0 && <div className="discussion-note-list">{notes.map((note) => <div key={note.id}><strong>{discussionOpen ? note.author_display_name || "A club member" : "Your note"}</strong><p>{note.content}</p></div>)}</div>}{message && <p className="reading-message">{message}</p>}</div>;
}

function PastCycleNotes({ cycleId, count }: { cycleId: number; count: number }) {
  const [open, setOpen] = useState(false); const [notes, setNotes] = useState<DiscussionNote[]>([]); const [message, setMessage] = useState("");
  async function toggle() { if (open) { setOpen(false); return; } const token = localStorage.getItem("tomeys_token"); if (!token) return; try { setNotes(await getCycleDiscussionNotes(cycleId, token)); setOpen(true); } catch (error) { setMessage(error instanceof Error ? error.message : "Could not load discussion notes."); } }
  return <div className="past-cycle-notes"><button type="button" onClick={toggle}>{open ? "Hide discussion notes" : `${count} discussion note${count === 1 ? "" : "s"} saved`}</button>{open && <div className="discussion-note-list">{notes.length ? notes.map((note) => <div key={note.id}><strong>{note.author_display_name || "A club member"}</strong><p>{note.content}</p></div>) : <p>No discussion notes were saved for this cycle.</p>}</div>}{message && <p className="reading-message">{message}</p>}</div>;
}

function SuggestionsCard({ club, clubId, suggestions, onSubmitted }: { club: ClubDashboard; clubId: string; suggestions: Suggestion[]; onSubmitted: () => void }) {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const participationCycle = club.participation_cycle;
  const votingOpen = participationCycle?.phase === "voting";
  const suggestionsOpen = participationCycle?.phase === "suggestion";
  const hasSubmittedVotes = suggestions.some((suggestion) => suggestion.can_view_vote_totals);
  const votesRemaining = club.club.max_votes_per_user - selectedIds.length;
  function toggleSuggestion(suggestionId: number) { setMessage(""); setSelectedIds((current) => current.includes(suggestionId) ? current.filter((id) => id !== suggestionId) : current.length < club.club.max_votes_per_user ? [...current, suggestionId] : current); }
  async function submitVotes() { const token = localStorage.getItem("tomeys_token"); if (!token || !selectedIds.length) return; setSubmitting(true); try { for (const suggestionId of selectedIds) await castSuggestionVote(suggestionId, token); setSelectedIds([]); setMessage("Your votes have been cast."); onSubmitted(); } catch (error) { setMessage(error instanceof Error ? error.message : "Could not submit your votes."); } finally { setSubmitting(false); } }
  return <article className="dashboard-card suggestions-card"><div className="card-heading"><p className="eyebrow">{participationCycle?.name ? `${participationCycle.name} suggestions` : "Book suggestions"}</p><span>{suggestions.length} in the running</span></div>{suggestionsOpen && <Link className="quiet-link" to={`/books?clubId=${clubId}`}>Suggest a book →</Link>}{votingOpen && !hasSubmittedVotes && <div className="vote-ballot"><p>Select up to {club.club.max_votes_per_user} book{club.club.max_votes_per_user === 1 ? "" : "s"}. {votesRemaining} remaining.</p></div>}{suggestions.length ? suggestions.map((suggestion) => <div className="suggestion-row" key={suggestion.id}>{votingOpen && !hasSubmittedVotes && <label className="vote-checkbox"><input type="checkbox" checked={selectedIds.includes(suggestion.id)} disabled={submitting || (!selectedIds.includes(suggestion.id) && selectedIds.length >= club.club.max_votes_per_user)} onChange={() => toggleSuggestion(suggestion.id)} /><span className="sr-only">Vote for {suggestion.book.title}</span></label>}<div className="suggestion-book">{suggestion.book.title.charAt(0)}</div><div><h2>{suggestion.book.title}</h2><p>{suggestion.book.authors || "Author unknown"}</p>{suggestion.book.description && <p className="suggestion-description">{suggestion.book.description}</p>}</div>{suggestion.can_view_vote_totals && <span className="vote-count">{suggestion.vote_count} vote{suggestion.vote_count === 1 ? "" : "s"}</span>}</div>) : <EmptyState text={suggestionsOpen ? "There are no suggestions for this cycle yet. Make the first recommendation." : "There are no suggestions in the current voting cycle."} />}{votingOpen && !hasSubmittedVotes && <button className="submit-votes" disabled={submitting || !selectedIds.length} type="button" onClick={submitVotes}>{submitting ? "Casting votes…" : `Submit ${selectedIds.length || ""} vote${selectedIds.length === 1 ? "" : "s"}`}</button>}{votingOpen && hasSubmittedVotes && <p className="reading-message">Your votes have been cast. Totals are now visible.</p>}{message && <p className="reading-message">{message}</p>}</article>;
}

function localDateTimeParts(timestamp?: string | null) {
  if (!timestamp) return { date: "", time: "" };
  const utcTimestamp = /(?:Z|[+-]\d{2}:\d{2})$/.test(timestamp) ? timestamp : `${timestamp}Z`;
  const date = new Date(utcTimestamp);
  const pad = (value: number) => String(value).padStart(2, "0");
  return { date: `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`, time: `${pad(date.getHours())}:${pad(date.getMinutes())}` };
}

function formatLocalDateTime(timestamp?: string | null) {
  if (!timestamp) return "To be decided";
  const utcTimestamp = /(?:Z|[+-]\d{2}:\d{2})$/.test(timestamp) ? timestamp : `${timestamp}Z`;
  return new Date(utcTimestamp).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function cycleFormValues(data: FormData) {
  const asIso = (name: string) => { let hour = Number(data.get(`${name}Hour`)); const meridiem = String(data.get(`${name}Meridiem`)); if (meridiem === "PM" && hour !== 12) hour += 12; if (meridiem === "AM" && hour === 12) hour = 0; return new Date(`${String(data.get(`${name}Date`))}T${String(hour).padStart(2, "0")}:${String(data.get(`${name}Minute`))}`).toISOString(); };
  return { name: String(data.get("name") || ""), suggestion_start_date: asIso("suggestion"), voting_start_date: asIso("voting"), voting_end_date: asIso("voteEnd"), discussion_date: asIso("discussion") };
}

function CycleFields({ defaults }: { defaults?: { name: string | null; suggestion_start_date: string | null; voting_start_date: string | null; voting_end_date: string | null; discussion_date: string | null } }) {
  const suggestion = localDateTimeParts(defaults?.suggestion_start_date); const voting = localDateTimeParts(defaults?.voting_start_date); const voteEnd = localDateTimeParts(defaults?.voting_end_date); const discussion = localDateTimeParts(defaults?.discussion_date);
  const scheduleField = (label: string, name: string, value: { date: string; time: string }) => { const [hour = "00", minute = "00"] = value.time.split(":"); const hourNumber = Number(hour); const displayHour = String(hourNumber % 12 || 12); const meridiem = hourNumber >= 12 ? "PM" : "AM"; return <label className="cycle-schedule-field"><span>{label}</span><div><input required type="date" name={`${name}Date`} defaultValue={value.date} /><div className="cycle-time-selects"><select required name={`${name}Hour`} defaultValue={displayHour}>{Array.from({ length: 12 }, (_, index) => String(index + 1)).map((option) => <option key={option} value={option}>{option}</option>)}</select><span>:</span><select required name={`${name}Minute`} defaultValue={minute}>{["00", "15", "30", "45"].map((option) => <option key={option} value={option}>{option}</option>)}</select><select required name={`${name}Meridiem`} defaultValue={meridiem}><option value="AM">AM</option><option value="PM">PM</option></select></div></div></label>; };
  return <><input name="name" defaultValue={defaults?.name || ""} placeholder="Cycle name (optional)" />{scheduleField("Suggestions start", "suggestion", suggestion)}{scheduleField("Voting starts", "voting", voting)}{scheduleField("Voting ends", "voteEnd", voteEnd)}{scheduleField("Discussion", "discussion", discussion)}</>;
}

function ControlDrawer({ club, role, clubId, onSaved }: { club: ClubDashboard; role: string; clubId: string; onSaved: () => void }) {
  const [open, setOpen] = useState(false); const [requests, setRequests] = useState<JoinRequest[]>([]); const [message, setMessage] = useState(""); const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("tomeys_token");
  useEffect(() => { if (open && token) getJoinRequests(clubId, token).then(setRequests).catch((err: Error) => setMessage(err.message)); }, [clubId, open, token]);
  async function decide(request: JoinRequest, approved: boolean) { if (!token) return; setBusy(true); try { await decideJoinRequest(request.id, approved, token); setRequests((current) => current.filter((item) => item.id !== request.id)); setMessage(approved ? "Join request approved." : "Join request rejected."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not process request."); } finally { setBusy(false); } }
  async function promote(username: string) { if (!token) return; setBusy(true); try { await updateMemberRole(clubId, username, "admin", token); setMessage(`${username} is now an admin.`); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not update role."); } finally { setBusy(false); } }
  async function saveCycle(event: React.FormEvent<HTMLFormElement>, future: boolean) { event.preventDefault(); if (!token) return; const values = cycleFormValues(new FormData(event.currentTarget)); setBusy(true); try { if (future) await createCycle(clubId, values, token); else if (club.active_cycle) await updateCycle(club.active_cycle.id, values, token); setMessage(future ? "Future cycle scheduled." : "Current cycle updated."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not save cycle."); } finally { setBusy(false); } }
  async function updateFutureCycle(event: React.FormEvent<HTMLFormElement>, cycleId: number) { event.preventDefault(); if (!token) return; setBusy(true); try { await updateCycle(cycleId, cycleFormValues(new FormData(event.currentTarget)), token); setMessage("Scheduled cycle updated."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not update scheduled cycle."); } finally { setBusy(false); } }
  return <><button className="club-controls-trigger" onClick={() => setOpen(true)}>Club controls</button>{open && <div className="control-overlay" role="dialog" aria-modal="true" aria-label="Club controls"><button className="control-scrim" aria-label="Close controls" onClick={() => setOpen(false)} /><aside className="control-drawer"><button className="drawer-close" onClick={() => setOpen(false)}>×</button><p className="eyebrow">{role} controls</p><h2>Club controls</h2><section><h3>Join requests</h3>{requests.length ? requests.map((request) => <div className="request-row" key={request.id}><span>Reader #{request.user_id}</span><button disabled={busy} onClick={() => decide(request, true)}>Accept</button><button disabled={busy} onClick={() => decide(request, false)}>Reject</button></div>) : <p>No pending requests.</p>}</section><InvitePanel clubId={clubId} />{club.active_cycle && <form className="manage-form" onSubmit={(event) => saveCycle(event, false)}><h3>Edit current cycle</h3><CycleFields defaults={club.active_cycle} /><button disabled={busy}>Save cycle</button></form>}{club.future_cycles.map((cycle) => <form className="manage-form" key={cycle.id} onSubmit={(event) => updateFutureCycle(event, cycle.id)}><h3>Edit scheduled cycle</h3><CycleFields defaults={cycle} /><button disabled={busy}>Save scheduled cycle</button></form>)}<form className="manage-form" onSubmit={(event) => saveCycle(event, true)}><h3>Schedule a future cycle</h3><CycleFields /><button disabled={busy}>Schedule cycle</button></form><ManagementPanel club={{ ...club, viewer_role: role }} clubId={clubId} onSaved={onSaved} />{message && <p className="reading-message">{message}</p>}</aside></div>}</>;
}

function InvitePanel({ clubId }: { clubId: string }) {
  const [invitations, setInvitations] = useState<ClubInvitation[]>([]);
  const [username, setUsername] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("tomeys_token");

  const refresh = () => { if (token) getClubInvitations(clubId, token).then(setInvitations).catch(() => undefined); };
  useEffect(refresh, [clubId]);

  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !username.trim()) return;
    setBusy(true); setMessage("");
    try {
      await inviteMember(clubId, username.trim(), token);
      setUsername("");
      setMessage("Invitation sent.");
      refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not send that invitation."); } finally { setBusy(false); }
  }

  async function revoke(invitationId: number) {
    if (!token) return;
    setBusy(true);
    try { await revokeInvitation(invitationId, token); setMessage("Invitation revoked."); refresh(); } catch (error) { setMessage(error instanceof Error ? error.message : "Could not revoke that invitation."); } finally { setBusy(false); }
  }

  return <section><h3>Invite a reader</h3><form className="manage-form" onSubmit={send}><label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="theirhandle" /></label><button disabled={busy || !username.trim()}>Send invitation</button></form>{invitations.length > 0 && <div className="request-list"><p className="eyebrow">Awaiting a reply</p>{invitations.map((invitation) => <div className="request-row" key={invitation.id}><span>{invitation.invited_display_name || invitation.invited_username}</span><button disabled={busy} onClick={() => revoke(invitation.id)}>Revoke</button></div>)}</div>}{message && <p className="reading-message">{message}</p>}</section>;
}

function ManagementPanel({ club, clubId, onSaved }: { club: ClubDashboard; clubId: string; onSaved: () => void }) {
  const [message, setMessage] = useState(""); const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("tomeys_token"); const owner = club.viewer_role === "owner";
  async function startCycle(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (!token) return; setBusy(true); try { await createCycle(clubId, cycleFormValues(new FormData(event.currentTarget)), token); setMessage("New cycle started."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not start cycle."); } finally { setBusy(false); } }
  async function saveSettings(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); if (!token) return; const data = new FormData(event.currentTarget); setBusy(true); try { await updateClubSettings(clubId, { is_public: data.get("visibility") === "public", join_policy: String(data.get("policy")), max_votes_per_user: Number(data.get("votes")) }, token); setMessage("Club settings saved."); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not save settings."); } finally { setBusy(false); } }
  async function promote(username: string) { if (!token) return; setBusy(true); try { await updateMemberRole(clubId, username, "admin", token); setMessage(`${username} is now an admin.`); onSaved(); } catch (err) { setMessage(err instanceof Error ? err.message : "Could not update role."); } finally { setBusy(false); } }
  return <section className="management-panel"><p className="eyebrow">{owner ? "Owner controls" : "Admin controls"}</p><h2>Manage this club</h2>{!club.active_cycle && <form className="manage-form cycle-form" onSubmit={startCycle}><h3>Start the next cycle</h3><CycleFields /><button disabled={busy}>Start cycle</button></form>}{owner && <><form className="manage-form" onSubmit={saveSettings}><h3>Club settings</h3><label>Visibility<select name="visibility" defaultValue={club.club.is_public ? "public" : "private"}><option value="public">Public</option><option value="private">Private</option></select></label><label>Joining<select name="policy" defaultValue={club.club.join_policy}><option value="open">Open — join instantly</option><option value="request">Request approval</option></select></label><label>Votes per member<input name="votes" type="number" min="1" defaultValue={club.club.max_votes_per_user} /></label><button disabled={busy}>Save settings</button></form><div className="manage-form"><h3>Promote members</h3>{club.members.filter((member) => member.role === "member").map((member) => <div className="promote-row" key={member.username}><span>{member.display_name || member.username}</span><button disabled={busy} onClick={() => promote(member.username)}>Make admin</button></div>)}</div></>}{message && <p className="reading-message">{message}</p>}</section>;
}
