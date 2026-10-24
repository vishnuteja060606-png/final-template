from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import get_current_user, require_role
from app.models.user import User
from app.models.creator import CreatorProfile
from app.schemas.connection import ConnectionStatusUpdate, ConnectionResponse, CreatorConnectionsSummary
from app.services.connection_service import connection_service

router = APIRouter(tags=["Connections"])

@router.post("/api/creators/{target_creator_id}/connect", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
def request_connection(
    target_creator_id: int,
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Reviewer Feature: Creator sends mutual networking connection request to another creator.
    """
    conn = connection_service.send_connection_request(db, current_user.id, target_creator_id)
    return connection_service._to_response(conn)

@router.post("/api/connections/{connection_id}/status", response_model=ConnectionResponse)
@router.put("/api/connections/{connection_id}/status", response_model=ConnectionResponse)
@router.post("/api/creators/connections/{connection_id}/respond", response_model=ConnectionResponse)
@router.put("/api/creators/connections/{connection_id}/respond", response_model=ConnectionResponse)
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
    return connection_service._to_response(conn)

@router.get("/api/creators/{creator_id}/connections", response_model=CreatorConnectionsSummary)
def list_connections(
    creator_id: int,
    db: Session = Depends(get_db)
):
    """
    List all accepted connections for a creator profile.
    """
    return connection_service.get_creator_connections(db, creator_id)

@router.get("/api/connections/pending", response_model=list[ConnectionResponse])
def get_incoming_pending_connections(
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    """
    List all pending connection requests received by the currently authenticated creator.
    """
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator profile not found.")
    return connection_service.get_pending_incoming_requests(db, profile.id)

@router.get("/api/connections/sent", response_model=list[ConnectionResponse])
def get_outgoing_pending_connections(
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    """
    List all pending connection requests sent by the currently authenticated creator.
    """
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator profile not found.")
    return connection_service.get_pending_outgoing_requests(db, profile.id)
