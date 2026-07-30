import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getProfileSettings, ProfileSettings, updateProfileSettings } from "../lib/api";
import { AppHeader } from "../components/AppHeader";

export function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ProfileSettings | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [clubUpdates, setClubUpdates] = useState(true);
  const [cycleReminders, setCycleReminders] = useState(true);
  const [readingActivity, setReadingActivity] = useState(true);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => { const token = localStorage.getItem("tomeys_token"); if (!token) { navigate("/auth", { replace: true }); return; } getProfileSettings(token).then((result) => { setProfile(result); setDisplayName(result.display_name || ""); setClubUpdates(result.club_updates); setCycleReminders(result.cycle_reminders); setReadingActivity(result.reading_activity); }).catch((error: Error) => setMessage(error.message)); }, [navigate]);
  async function save(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const token = localStorage.getItem("tomeys_token"); if (!token) return; setSaving(true); setMessage(""); try { const result = await updateProfileSettings({ display_name: displayName, club_updates: clubUpdates, cycle_reminders: cycleReminders, reading_activity: readingActivity }, token); setProfile(result); setMessage("Profile settings saved."); } catch (error) { setMessage(error instanceof Error ? error.message : "Could not save profile settings."); } finally { setSaving(false); } }

  if (!profile) return <main className="map-page"><p className="loading-ink">Opening your profile…</p></main>;
  return <main className="dashboard-page profile-page"><AppHeader /><section className="search-hero"><p className="eyebrow">Your reader profile</p><h1>{profile.display_name || profile.username}</h1><p>Set how Tomeys knows you and which reading moments you want to hear about.</p></section><form className="profile-form" onSubmit={save}><section><h2>Identity</h2><p className="profile-username">@{profile.username}</p><label>Display name<input value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="How readers know you" maxLength={80} /></label></section><section><h2>Notifications</h2><p>Choose the updates you’d like Tomeys to send when delivery channels are connected.</p><label className="preference-toggle"><input type="checkbox" checked={clubUpdates} onChange={(event) => setClubUpdates(event.target.checked)} /><span><strong>Club updates</strong>New members, requests, and club changes.</span></label><label className="preference-toggle"><input type="checkbox" checked={cycleReminders} onChange={(event) => setCycleReminders(event.target.checked)} /><span><strong>Cycle reminders</strong>Suggestion, voting, and discussion milestones.</span></label><label className="preference-toggle"><input type="checkbox" checked={readingActivity} onChange={(event) => setReadingActivity(event.target.checked)} /><span><strong>Reading activity</strong>Notes and reviews connected to your reads.</span></label></section><button disabled={saving}>{saving ? "Saving…" : "Save profile"}</button>{message && <p className="reading-message">{message}</p>}</form></main>;
}
