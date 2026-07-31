from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.dependencies import get_db
from app.models.invitation import ClubInvitation
from app.models.user import User
from app.schemas.invitation import (
    ClubInvitationResponse,
    InvitationCreate,
    InvitationResponse,
)
from app.services.invitation_service import (
    accept_invitation,
    create_invitation,
    decline_invitation,
    get_club_invitations,
    get_user_invitations,
    revoke_invitation,
)

router = APIRouter(
    tags=["Invitations"],
)


def for_recipient(invitation: ClubInvitation) -> ClubInvitation:
    invitation.club_name = invitation.club.name
    invitation.invited_by_username = (
        invitation.invited_by.display_name or invitation.invited_by.username
    )

    return invitation


def for_admin(invitation: ClubInvitation) -> ClubInvitation:
    invitation.invited_username = invitation.invited_user.username
    invitation.invited_display_name = invitation.invited_user.display_name

    return invitation


@router.post(
    "/clubs/{club_id}/invitations",
    response_model=ClubInvitationResponse,
)
def invite_member(
    club_id: int,
    invitation: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invite an existing reader to a club. Owners and admins only.
    """

    return for_admin(
        create_invitation(
            db,
            club_id,
            current_user.id,
            invitation.username,
        )
    )


@router.get(
    "/clubs/{club_id}/invitations",
    response_model=list[ClubInvitationResponse],
)
def list_club_invitations(
    club_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invitations this club has sent that are still pending.
    """

    return [
        for_admin(invitation)
        for invitation in get_club_invitations(
            db,
            club_id,
            current_user.id,
        )
    ]


@router.get(
    "/invitations",
    response_model=list[InvitationResponse],
)
def list_my_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Invitations waiting for the signed-in reader.
    """

    return [
        for_recipient(invitation)
        for invitation in get_user_invitations(
            db,
            current_user.id,
        )
    ]


@router.post(
    "/invitations/{invitation_id}/accept",
    response_model=InvitationResponse,
)
def accept(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return for_recipient(
        accept_invitation(
            db,
            invitation_id,
            current_user.id,
        )
    )


@router.post(
    "/invitations/{invitation_id}/decline",
    response_model=InvitationResponse,
)
def decline(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return for_recipient(
        decline_invitation(
            db,
            invitation_id,
            current_user.id,
        )
    )


@router.delete(
    "/invitations/{invitation_id}",
)
def revoke(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Withdraw a pending invitation. Owners and admins only.
    """

    revoke_invitation(
        db,
        invitation_id,
        current_user.id,
    )

    return {
        "message": "Invitation revoked",
    }
