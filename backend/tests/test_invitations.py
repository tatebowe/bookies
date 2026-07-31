"""Club invitations: a club asking a user to join.

The mirror of join requests. Only owners and admins may invite, only the
recipient may answer, and an invitation reveals nothing about the club
beyond its name until it is accepted.
"""

from datetime import datetime, timedelta, timezone


def auth(client, username, email):
    assert (
        client.post(
            "/users/",
            json={
                "username": username,
                "email": email,
                "password": "password123",
            },
        ).status_code
        == 200
    )

    token = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "password123",
        },
    ).json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def make_club(client, headers, name="Invite Only", join_policy="invite"):
    response = client.post(
        "/clubs/",
        headers=headers,
        json={
            "name": name,
            "is_public": False,
            "join_policy": join_policy,
        },
    )

    assert response.status_code == 200

    return response.json()


def invite(client, headers, club_id, username):
    return client.post(
        f"/clubs/{club_id}/invitations",
        headers=headers,
        json={"username": username},
    )


def club_names_for(client, headers):
    return [club["name"] for club in client.get("/clubs/", headers=headers).json()]


def setup_club_and_guest(client):
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner)
    guest = auth(client, "guest", "guest@example.com")

    return owner, club, guest


# --- sending -------------------------------------------------------------


def test_admin_can_invite_an_existing_user(client):
    owner, club, guest = setup_club_and_guest(client)

    response = invite(client, owner, club["id"], "guest")

    assert response.status_code == 200
    assert response.json()["invited_username"] == "guest"
    assert response.json()["status"] == "pending"


def test_non_member_cannot_invite(client):
    owner, club, guest = setup_club_and_guest(client)
    outsider = auth(client, "outsider", "outsider@example.com")

    assert invite(client, outsider, club["id"], "guest").status_code == 403


def test_plain_member_cannot_invite(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()
    client.post(f"/invitations/{invitation['id']}/accept", headers=guest)

    auth(client, "third", "third@example.com")

    assert invite(client, guest, club["id"], "third").status_code == 403


def test_promoted_admin_can_invite(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()
    client.post(f"/invitations/{invitation['id']}/accept", headers=guest)

    promote = client.patch(
        f"/clubs/{club['id']}/members/guest/role",
        headers=owner,
        json={"role": "admin"},
    )
    assert promote.status_code == 200

    auth(client, "third", "third@example.com")

    assert invite(client, guest, club["id"], "third").status_code == 200


def test_cannot_invite_an_unknown_username(client):
    owner, club, guest = setup_club_and_guest(client)

    assert invite(client, owner, club["id"], "nobody").status_code == 404


def test_cannot_invite_yourself(client):
    owner, club, guest = setup_club_and_guest(client)

    assert invite(client, owner, club["id"], "owner").status_code == 400


def test_cannot_invite_an_existing_member(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()
    client.post(f"/invitations/{invitation['id']}/accept", headers=guest)

    assert invite(client, owner, club["id"], "guest").status_code == 409


def test_cannot_send_a_duplicate_pending_invitation(client):
    owner, club, guest = setup_club_and_guest(client)
    invite(client, owner, club["id"], "guest")

    assert invite(client, owner, club["id"], "guest").status_code == 409


# --- answering -----------------------------------------------------------


def test_recipient_sees_only_the_club_name(client):
    owner, club, guest = setup_club_and_guest(client)
    invite(client, owner, club["id"], "guest")

    mine = client.get("/invitations", headers=guest).json()

    assert len(mine) == 1
    assert mine[0]["club_name"] == "Invite Only"
    assert "description" not in mine[0]
    assert "members" not in mine[0]


def test_pending_invitation_grants_no_club_access(client):
    """Invited is not joined: the club stays closed until acceptance."""
    owner, club, guest = setup_club_and_guest(client)
    invite(client, owner, club["id"], "guest")

    club_id = club["id"]

    assert client.get(f"/clubs/{club_id}/dashboard", headers=guest).status_code == 403
    assert client.get(f"/clubs/{club_id}/members", headers=guest).status_code == 403
    assert client.get(f"/clubs/{club_id}/history", headers=guest).status_code == 403


def test_accepting_joins_the_club(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    response = client.post(f"/invitations/{invitation['id']}/accept", headers=guest)

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert club_names_for(client, guest) == ["Invite Only"]

    dashboard = client.get(f"/clubs/{club['id']}/dashboard", headers=guest)
    assert dashboard.status_code == 200


def test_accepting_works_despite_the_invite_join_policy(client):
    """POST /clubs/{id}/join is refused on an invite club; the invite is not."""
    owner, club, guest = setup_club_and_guest(client)

    assert client.post(f"/clubs/{club['id']}/join", headers=guest).status_code == 400

    invitation = invite(client, owner, club["id"], "guest").json()

    accept = client.post(f"/invitations/{invitation['id']}/accept", headers=guest)
    assert accept.status_code == 200


def test_declining_does_not_join(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    response = client.post(f"/invitations/{invitation['id']}/decline", headers=guest)

    assert response.status_code == 200
    assert club_names_for(client, guest) == []


def test_someone_else_cannot_answer_your_invitation(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    intruder = auth(client, "intruder", "intruder@example.com")

    accept = client.post(f"/invitations/{invitation['id']}/accept", headers=intruder)

    assert accept.status_code == 403
    assert club_names_for(client, intruder) == []


def test_an_invitation_cannot_be_answered_twice(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    client.post(f"/invitations/{invitation['id']}/decline", headers=guest)

    accept = client.post(f"/invitations/{invitation['id']}/accept", headers=guest)
    assert accept.status_code == 400


def test_answering_requires_authentication(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    assert client.post(f"/invitations/{invitation['id']}/accept").status_code == 401


def test_unknown_invitation_is_404(client):
    guest = auth(client, "guest", "guest@example.com")

    assert client.post("/invitations/999999/accept", headers=guest).status_code == 404


# --- re-inviting and revoking --------------------------------------------


def test_a_declined_invitation_can_be_sent_again(client):
    owner, club, guest = setup_club_and_guest(client)
    first = invite(client, owner, club["id"], "guest").json()
    client.post(f"/invitations/{first['id']}/decline", headers=guest)

    second = invite(client, owner, club["id"], "guest")

    assert second.status_code == 200
    assert second.json()["id"] != first["id"]


def test_admin_can_revoke_a_pending_invitation(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    assert (
        client.delete(f"/invitations/{invitation['id']}", headers=owner).status_code
        == 200
    )
    assert client.get("/invitations", headers=guest).json() == []


def test_a_revoked_invitation_cannot_be_accepted(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()
    client.delete(f"/invitations/{invitation['id']}", headers=owner)

    accept = client.post(f"/invitations/{invitation['id']}/accept", headers=guest)

    assert accept.status_code == 400
    assert club_names_for(client, guest) == []


def test_recipient_cannot_revoke(client):
    owner, club, guest = setup_club_and_guest(client)
    invitation = invite(client, owner, club["id"], "guest").json()

    assert (
        client.delete(f"/invitations/{invitation['id']}", headers=guest).status_code
        == 403
    )


# --- admin listing -------------------------------------------------------


def test_admins_see_pending_invitations_for_their_club(client):
    owner, club, guest = setup_club_and_guest(client)
    invite(client, owner, club["id"], "guest")

    pending = client.get(f"/clubs/{club['id']}/invitations", headers=owner).json()

    assert [row["invited_username"] for row in pending] == ["guest"]


def test_outsiders_cannot_list_a_clubs_invitations(client):
    owner, club, guest = setup_club_and_guest(client)
    invite(client, owner, club["id"], "guest")

    assert (
        client.get(f"/clubs/{club['id']}/invitations", headers=guest).status_code == 403
    )


def test_invitations_are_scoped_to_the_recipient(client):
    owner, club, guest = setup_club_and_guest(client)
    invite(client, owner, club["id"], "guest")

    other = auth(client, "other", "other@example.com")

    assert client.get("/invitations", headers=other).json() == []


# --- joining hooks into the active reading -------------------------------


def test_accepting_mid_cycle_creates_a_reading_entry(client, mock_google_book):
    """The bug this would otherwise reintroduce: joining without a reading."""
    owner = auth(client, "owner", "owner@example.com")
    club = make_club(client, owner, name="Reading Club")

    book = client.post(
        "/books/",
        headers=owner,
        json={"google_books_id": "the-hobbit-test-id"},
    ).json()

    now = datetime.now(timezone.utc)

    # Open for suggestions right now, so the book can be put forward...
    cycle = client.post(
        f"/clubs/{club['id']}/cycles",
        headers=owner,
        json={
            "suggestion_start_date": (now - timedelta(hours=1)).isoformat(),
            "voting_start_date": (now + timedelta(days=1)).isoformat(),
            "voting_end_date": (now + timedelta(days=2)).isoformat(),
            "discussion_date": (now + timedelta(days=10)).isoformat(),
        },
    )
    assert cycle.status_code == 200

    suggestion = client.post(
        f"/clubs/{club['id']}/suggestions",
        headers=owner,
        json={"book_id": book["id"], "anonymous": False},
    )
    assert suggestion.status_code == 200

    # ...then slide the window into the past so voting closes and the cycle
    # finalises into its reading phase with that book selected.
    reschedule = client.patch(
        f"/clubs/cycles/{cycle.json()['id']}",
        headers=owner,
        json={
            "suggestion_start_date": (now - timedelta(days=5)).isoformat(),
            "voting_start_date": (now - timedelta(days=4)).isoformat(),
            "voting_end_date": (now - timedelta(days=3)).isoformat(),
            "discussion_date": (now + timedelta(days=10)).isoformat(),
        },
    )
    assert reschedule.status_code == 200

    active = client.get(f"/clubs/{club['id']}/cycles/active", headers=owner)
    assert active.status_code == 200
    assert active.json()["phase"] == "reading"
    assert active.json()["selected_book_id"] == book["id"]

    guest = auth(client, "guest", "guest@example.com")
    invitation = invite(client, owner, club["id"], "guest").json()

    accept = client.post(f"/invitations/{invitation['id']}/accept", headers=guest)
    assert accept.status_code == 200

    entries = client.get("/reading-entries/", headers=guest).json()

    assert [entry["book_id"] for entry in entries] == [book["id"]]
