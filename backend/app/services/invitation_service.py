from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.exceptions.invitation_exceptions import (
    InvalidInvitationError,
    InvitationAlreadyExistsError,
    InvitationNotFoundError,
    UnauthorizedInvitationError,
)
from app.exceptions.user_exceptions import UserNotFoundError
from app.models.invitation import ClubInvitation
from app.services.club_service import get_club_by_id
from app.services.helpers import get_by_id, save_and_refresh
from app.services.membership_service import grant_membership
from app.services.permission_service import get_membership, require_club_admin
from app.services.user_service import get_user_by_username


def get_pending_invitation(
    db: Session,
    club_id: int,
    user_id: int,
) -> ClubInvitation | None:

    return (
        db.query(ClubInvitation)
        .filter(
            ClubInvitation.club_id == club_id,
            ClubInvitation.invited_user_id == user_id,
            ClubInvitation.status == "pending",
        )
        .first()
    )


def create_invitation(
    db: Session,
    club_id: int,
    inviter_id: int,
    username: str,
) -> ClubInvitation:
    """
    Invite an existing user to a club.

    Requires admin privileges. A previously declined invitation does not
    block a new one, so an admin can ask again later.

    Raises:
        NotClubAdminError: If the inviter does not administer the club.
        UserNotFoundError: If no user has that username.
        InvalidInvitationError: If the admin invites themselves.
        InvitationAlreadyExistsError:
            If the user is already a member or already has one pending.
    """

    require_club_admin(
        db,
        club_id,
        inviter_id,
    )

    club = get_club_by_id(
        db,
        club_id,
    )

    user = get_user_by_username(
        db,
        username,
    )

    if user is None:
        raise UserNotFoundError("User not found")

    if user.id == inviter_id:
        raise InvalidInvitationError("You are already a member of this club")

    if get_membership(db, club.id, user.id) is not None:
        raise InvitationAlreadyExistsError("User is already a member of this club")

    if get_pending_invitation(db, club.id, user.id) is not None:
        raise InvitationAlreadyExistsError(
            "User already has a pending invitation to this club"
        )

    invitation = ClubInvitation(
        club_id=club.id,
        invited_user_id=user.id,
        invited_by_user_id=inviter_id,
        status="pending",
    )

    return save_and_refresh(
        db,
        invitation,
    )


def get_invitation_by_id(
    db: Session,
    invitation_id: int,
) -> ClubInvitation:

    invitation = get_by_id(
        db,
        ClubInvitation,
        invitation_id,
    )

    if invitation is None:
        raise InvitationNotFoundError("Invitation not found")

    return invitation


def get_user_invitations(
    db: Session,
    user_id: int,
) -> list[ClubInvitation]:
    """
    Pending invitations addressed to this user.
    """

    return (
        db.query(ClubInvitation)
        .filter(
            ClubInvitation.invited_user_id == user_id,
            ClubInvitation.status == "pending",
        )
        .order_by(ClubInvitation.created_at)
        .all()
    )


def get_club_invitations(
    db: Session,
    club_id: int,
    user_id: int,
) -> list[ClubInvitation]:
    """
    Pending invitations a club has sent. Admins only.
    """

    require_club_admin(
        db,
        club_id,
        user_id,
    )

    return (
        db.query(ClubInvitation)
        .filter(
            ClubInvitation.club_id == club_id,
            ClubInvitation.status == "pending",
        )
        .order_by(ClubInvitation.created_at)
        .all()
    )


def require_recipient(
    invitation: ClubInvitation,
    user_id: int,
) -> None:
    """
    Only the invited user may answer their own invitation.
    """

    if invitation.invited_user_id != user_id:
        raise UnauthorizedInvitationError("This invitation belongs to another user")

    if invitation.status != "pending":
        raise InvalidInvitationError("This invitation has already been answered")


def accept_invitation(
    db: Session,
    invitation_id: int,
    user_id: int,
) -> ClubInvitation:
    """
    Accept an invitation and join the club.

    An invitation is an explicit grant by an admin, so it admits the user
    whatever the club's join policy says.
    """

    invitation = get_invitation_by_id(
        db,
        invitation_id,
    )

    require_recipient(
        invitation,
        user_id,
    )

    if get_membership(db, invitation.club_id, user_id) is None:
        grant_membership(
            db,
            invitation.club_id,
            user_id,
        )

    invitation.status = "accepted"
    invitation.responded_at = datetime.now(timezone.utc)

    return save_and_refresh(
        db,
        invitation,
    )


def decline_invitation(
    db: Session,
    invitation_id: int,
    user_id: int,
) -> ClubInvitation:

    invitation = get_invitation_by_id(
        db,
        invitation_id,
    )

    require_recipient(
        invitation,
        user_id,
    )

    invitation.status = "declined"
    invitation.responded_at = datetime.now(timezone.utc)

    return save_and_refresh(
        db,
        invitation,
    )


def revoke_invitation(
    db: Session,
    invitation_id: int,
    user_id: int,
) -> ClubInvitation:
    """
    Withdraw an invitation before it is answered. Admins only.
    """

    invitation = get_invitation_by_id(
        db,
        invitation_id,
    )

    require_club_admin(
        db,
        invitation.club_id,
        user_id,
    )

    if invitation.status != "pending":
        raise InvalidInvitationError("This invitation has already been answered")

    invitation.status = "revoked"
    invitation.responded_at = datetime.now(timezone.utc)

    return save_and_refresh(
        db,
        invitation,
    )
