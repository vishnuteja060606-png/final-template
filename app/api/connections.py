from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.connection import ConnectionStatusUpdate, ConnectionResponse, CreatorConnectionsSummary
from app.services.connection_service import connection_service

router = APIRouter(tags=["Connections"])

@router.post("/api/creators/{target_creator_id}/connect", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
def request_connection(
    target_creator_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reviewer Feature: Creator sends connection request to another creator.
    """
    if current_user.role != "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can send creator-to-creator connection requests."
        )

    conn = connection_service.send_connection_request(db, current_user.id, target_creator_id)
    return ConnectionResponse(
        id=conn.id,
        requester_id=conn.requester_id,
        requester_name=conn.requester.display_name if conn.requester else "Creator",
        requester_avatar=conn.requester.profile_image_url if conn.requester else None,
        requester_specialization=conn.requester.specialization if conn.requester else None,
        receiver_id=conn.receiver_id,
        receiver_name=conn.receiver.display_name if conn.receiver else "Creator",
        receiver_avatar=conn.receiver.profile_image_url if conn.receiver else None,
        receiver_specialization=conn.receiver.specialization if conn.receiver else None,
        status=conn.status,
        created_at=conn.created_at,
        updated_at=conn.updated_at
    )

@router.post("/api/connections/{connection_id}/status", response_model=ConnectionResponse)
def update_connection(
    connection_id: int,
    data: ConnectionStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept or reject an incoming creator connection request.
    """
    conn = connection_service.update_connection_status(db, current_user.id, connection_id, data.action)
    return ConnectionResponse(
        id=conn.id,
        requester_id=conn.requester_id,
        requester_name=conn.requester.display_name if conn.requester else "Creator",
        requester_avatar=conn.requester.profile_image_url if conn.requester else None,
        requester_specialization=conn.requester.specialization if conn.requester else None,
        receiver_id=conn.receiver_id,
        receiver_name=conn.receiver.display_name if conn.receiver else "Creator",
        receiver_avatar=conn.receiver.profile_image_url if conn.receiver else None,
        receiver_specialization=conn.receiver.specialization if conn.receiver else None,
        status=conn.status,
        created_at=conn.created_at,
        updated_at=conn.updated_at
    )

@router.get("/api/creators/{creator_id}/connections", response_model=CreatorConnectionsSummary)
def list_connections(
    creator_id: int,
    db: Session = Depends(get_db)
):
    """
    List all accepted connections for a creator profile.
    """
    return connection_service.get_creator_connections(db, creator_id)
