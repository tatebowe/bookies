const apiBaseUrl = import.meta.env.VITE_API_URL ?? "/api";

export type Dashboard = {
  profile: { id: number; username: string; display_name: string | null; created_at: string };
  current_readings: Array<{ id: number; status: string; rating: number | null; review: string | null; finished_at: string | null; book: { id: number; title: string; authors: string | null }; club: { id: number; name: string } | null; club_reading_id: number | null }>;
  clubs: Array<{ club: { id: number; name: string }; role: string; active_cycle: { id: number; phase: string; active: boolean; voting_end_date: string | null } | null }>;
  history: Array<{ id: number; status: string; rating: number | null; review: string | null; finished_at: string | null; book: { id: number; title: string; authors: string | null }; club: { id: number; name: string } | null }>;
  notes: Array<{ id: number; title: string | null; content: string; created_at: string; book: { id: number; title: string; authors: string | null } | null }>;
};

export type ClubDashboard = {
  club: { id: number; name: string; description: string | null; is_public: boolean; join_policy: string; max_votes_per_user: number };
  current_book: { id: number; title: string; authors: string | null; suggested_by_display_name: string | null } | null;
  reading_progress: { not_started: number; reading: number; completed: number };
  members: Array<{ username: string; display_name: string | null; role: string }>;
  active_cycle: { id: number; name: string | null; phase: string; active: boolean; suggestion_start_date: string | null; voting_start_date: string | null; voting_end_date: string | null; discussion_date: string | null; selected_book: { id: number; title: string; authors: string | null } | null } | null;
  participation_cycle: { id: number; name: string | null; phase: string; active: boolean; suggestion_start_date: string | null; voting_start_date: string | null; voting_end_date: string | null; discussion_date: string | null } | null;
  future_cycles: Array<{ id: number; name: string | null; phase: string; active: boolean; suggestion_start_date: string | null; voting_start_date: string | null; voting_end_date: string | null; discussion_date: string | null }>;
  discussion_notes_count: number;
  viewer_role: string;
  viewer_club_reading_id: number | null;
};

export type Suggestion = { id: number; anonymous: boolean; vote_count: number; can_view_vote_totals: boolean; book: { id: number; title: string; authors: string | null; description: string | null; thumbnail_url: string | null } };
export type ClubHistory = { club_id: number; club_name: string; history: Array<{ cycle_id: number; cycle_name: string | null; book: { id: number; title: string; authors: string | null }; start_date: string; end_date: string; members_started: number; members_completed: number; discussion_notes_count: number }> };
export type DiscussionNote = { id: number; club_reading_id: number; title: string | null; content: string; created_at: string; updated_at: string; author_display_name: string | null };
export type ClubDiscovery = { id: number; name: string; description: string | null; is_public: boolean; join_policy: string; member_count: number };
export type BookSearchResult = { google_books_id: string; title: string; authors: string | null; description: string | null; thumbnail_url: string | null; published_date: string | null; categories: string | null };

async function request(path: string, init?: RequestInit) {
  const response = await fetch(`${apiBaseUrl}${path}`, init);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? "Something went wrong. Please try again.");
  }
  return response.json();
}

export async function login(emailOrUsername: string, password: string) {
  const form = new URLSearchParams({ username: emailOrUsername, password });
  return request("/auth/login", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: form });
}

export async function googleLogin(idToken: string) {
  return request("/auth/google", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token: idToken }) });
}

export async function register(input: { username: string; email: string; password: string; display_name: string }) {
  return request("/users/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input) });
}

export async function getDashboard(token: string): Promise<Dashboard> {
  return request("/dashboard", { headers: { Authorization: `Bearer ${token}` } });
}

export type ProfileSettings = { id: number; username: string; display_name: string | null; created_at: string; club_updates: boolean; cycle_reminders: boolean; reading_activity: boolean };
export async function getProfileSettings(token: string): Promise<ProfileSettings> {
  return request("/profiles/me", { headers: { Authorization: `Bearer ${token}` } });
}
export async function updateProfileSettings(data: Pick<ProfileSettings, "display_name" | "club_updates" | "cycle_reminders" | "reading_activity">, token: string): Promise<ProfileSettings> {
  return request("/profiles/me", { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(data) });
}

export async function getClubDashboard(clubId: string, token: string): Promise<ClubDashboard> {
  return request(`/clubs/${clubId}/dashboard`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function getSuggestions(clubId: string, token: string): Promise<Suggestion[]> {
  return request(`/clubs/${clubId}/suggestions`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function getClubHistory(clubId: string, token: string): Promise<ClubHistory> {
  return request(`/clubs/${clubId}/history`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function castSuggestionVote(suggestionId: number, token: string) {
  return request(`/suggestions/${suggestionId}/vote`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}
export async function getCycleDiscussionNotes(cycleId: number, token: string): Promise<DiscussionNote[]> {
  return request(`/clubs/readings/cycles/${cycleId}/discussion-notes`, { headers: { Authorization: `Bearer ${token}` } });
}
export async function createDiscussionNote(clubReadingId: number, content: string, token: string): Promise<DiscussionNote> {
  return request(`/clubs/readings/${clubReadingId}/notes`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ content }) });
}

export async function discoverClubs(query = ""): Promise<ClubDiscovery[]> {
  return request(query.trim() ? `/clubs/search?q=${encodeURIComponent(query.trim())}` : "/clubs/discover");
}

export async function joinClub(clubId: number, token: string): Promise<{ message: string; status?: string }> {
  return request(`/clubs/${clubId}/join`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}

export async function createClub(data: { name: string; description: string; is_public: boolean; join_policy: string; max_votes_per_user: number }, token: string) {
  return request("/clubs/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(data) });
}

export async function createCycle(clubId: string, data: { suggestion_start_date: string; voting_start_date: string; voting_end_date: string; discussion_date: string; name?: string }, token: string) {
  return request(`/clubs/${clubId}/cycles`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(data) });
}
export async function updateCycle(cycleId: number, data: { suggestion_start_date: string; voting_start_date: string; voting_end_date: string; discussion_date: string; name?: string }, token: string) {
  return request(`/clubs/cycles/${cycleId}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(data) });
}

export async function updateClubSettings(clubId: string, data: { is_public: boolean; join_policy: string; max_votes_per_user: number }, token: string) {
  return request(`/clubs/${clubId}/settings`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(data) });
}

export async function updateMemberRole(clubId: string, username: string, role: "member" | "admin", token: string) {
  return request(`/clubs/${clubId}/members/${encodeURIComponent(username)}/role`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ role }) });
}

export type Invitation = { id: number; club_id: number; club_name: string; invited_by_username: string; status: string; created_at: string };
export type ClubInvitation = { id: number; club_id: number; invited_username: string; invited_display_name: string | null; status: string; created_at: string };

export async function getMyInvitations(token: string): Promise<Invitation[]> {
  return request("/invitations", { headers: { Authorization: `Bearer ${token}` } });
}
export async function acceptInvitation(invitationId: number, token: string): Promise<Invitation> {
  return request(`/invitations/${invitationId}/accept`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}
export async function declineInvitation(invitationId: number, token: string): Promise<Invitation> {
  return request(`/invitations/${invitationId}/decline`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}
export async function getClubInvitations(clubId: string, token: string): Promise<ClubInvitation[]> {
  return request(`/clubs/${clubId}/invitations`, { headers: { Authorization: `Bearer ${token}` } });
}
export async function inviteMember(clubId: string, username: string, token: string): Promise<ClubInvitation> {
  return request(`/clubs/${clubId}/invitations`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ username }) });
}
export async function revokeInvitation(invitationId: number, token: string) {
  return request(`/invitations/${invitationId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
}

export type JoinRequest = { id: number; club_id: number; user_id: number; status: string; created_at: string };
export async function getJoinRequests(clubId: string, token: string): Promise<JoinRequest[]> {
  return request(`/clubs/${clubId}/join-requests`, { headers: { Authorization: `Bearer ${token}` } });
}
export async function decideJoinRequest(requestId: number, approved: boolean, token: string) {
  return request(`/clubs/join-requests/${requestId}/${approved ? "approve" : "reject"}`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
}

export async function searchBooks(query: string, token: string): Promise<BookSearchResult[]> {
  return request(`/books/search?q=${encodeURIComponent(query)}`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function addBookToReading(googleBooksId: string, token: string) {
  const book = await request("/books/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ google_books_id: googleBooksId }) });
  return request("/reading-entries/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ book_id: book.id, status: "not_started" }) });
}

export type UserClub = { id: number; name: string; description: string | null; is_public: boolean; join_policy: string; max_votes_per_user: number };
export async function getMyClubs(token: string): Promise<UserClub[]> {
  return request("/clubs/", { headers: { Authorization: `Bearer ${token}` } });
}

export async function suggestBook(clubId: number, googleBooksId: string, token: string) {
  const book = await request("/books/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ google_books_id: googleBooksId }) });
  return request(`/clubs/${clubId}/suggestions`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ book_id: book.id, anonymous: false }) });
}

export async function updateReadingStatus(readingEntryId: number, status: string, token: string) {
  return request(`/reading-entries/${readingEntryId}/status`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ status }) });
}

export async function saveReadingNote(readingEntryId: number, content: string, token: string) {
  return request("/reading-notes/", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ reading_entry_id: readingEntryId, content }) });
}

export async function saveReadingReview(readingEntryId: number, rating: number, review: string, token: string) {
  return request(`/reading-entries/${readingEntryId}/review`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ rating, review }) });
}

export async function getReadingEntry(readingEntryId: string, token: string) {
  return request(`/reading-entries/${readingEntryId}`, { headers: { Authorization: `Bearer ${token}` } });
}

export async function getReadingNotes(readingEntryId: string, token: string): Promise<Array<{ id: number; title: string | null; content: string; created_at: string }>> {
  return request(`/reading-notes/entry/${readingEntryId}`, { headers: { Authorization: `Bearer ${token}` } });
}
