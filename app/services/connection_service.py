import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from app.models.connection import CreatorConnection
from app.models.creator import CreatorProfile
from app.schemas.connection import ConnectionResponse, CreatorConnectionsSummary

logger = logging.getLogger(__name__)

class ConnectionService:
    def _to_response(self, c: CreatorConnection) -> ConnectionResponse:
        req_name = c.requester.display_name if c.requester else "Creator"
        req_avatar = c.requester.profile_image_url if c.requester else None
        req_spec = c.requester.specialization if c.requester else None

        rec_name = c.receiver.display_name if c.receiver else "Creator"
        rec_avatar = c.receiver.profile_image_url if c.receiver else None
        rec_spec = c.receiver.specialization if c.receiver else None

        return ConnectionResponse(
            id=c.id,
            requester_id=c.requester_id,
            requester_name=req_name,
            requester_avatar=req_avatar,
            requester_specialization=req_spec,
            receiver_id=c.receiver_id,
            receiver_name=rec_name,
            receiver_avatar=rec_avatar,
            receiver_specialization=rec_spec,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at
        )

    def send_connection_request(
        self, db: Session, requester_user_id: int, target_creator_id: int
    ) -> CreatorConnection:
        requester = db.query(CreatorProfile).filter(CreatorProfile.user_id == requester_user_id).first()
        if not requester:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered creators can initiate creator connections."
            )

        if requester.id == target_creator_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot connect with yourself."
            )

        target = db.query(CreatorProfile).filter(CreatorProfile.id == target_creator_id).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target creator not found.")

        # Check existing connection between the two creators
        existing = db.query(CreatorConnection).filter(
            or_(
                and_(CreatorConnection.requester_id == requester.id, CreatorConnection.receiver_id == target.id),
                and_(CreatorConnection.requester_id == target.id, CreatorConnection.receiver_id == requester.id)
            )
        ).first()

        if existing:
            if existing.status == "accepted":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already connected.")
            if existing.status == "pending":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A connection request is already pending.")
            # If rejected, allow re-requesting by resetting to pending
            existing.status = "pending"
            existing.requester_id = requester.id
            existing.receiver_id = target.id
            db.commit()
            db.refresh(existing)
            logger.info(f"Re-sent connection request from creator {requester.id} to {target.id}")
            return existing

        conn = CreatorConnection(
            requester_id=requester.id,
            receiver_id=target.id,
            status="pending"
        )
        db.add(conn)
        db.commit()
        db.refresh(conn)
        logger.info(f"Connection request sent from creator {requester.id} to {target.id}")
        return conn

    def update_connection_status(
        self, db: Session, user_id: int, connection_id: int, action: str
    ) -> CreatorConnection:
        creator = db.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()
        if not creator:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creator profile not found.")

        conn = db.query(CreatorConnection).filter(CreatorConnection.id == connection_id).first()
        if not conn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection request not found.")

        if conn.receiver_id != creator.id and conn.requester_id != creator.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this connection.")

        if action == "accept":
            # Only the recipient can accept an incoming request
            if conn.receiver_id != creator.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the recipient of a connection request can accept it."
                )
            conn.status = "accepted"
        elif action == "reject":
            conn.status = "rejected"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Allowed actions are 'accept' or 'reject'."
            )

        db.commit()
        db.refresh(conn)
        return conn

    def get_creator_connections(self, db: Session, creator_id: int) -> CreatorConnectionsSummary:
        creator = db.query(CreatorProfile).filter(CreatorProfile.id == creator_id).first()
        if not creator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found.")

        conns = db.query(CreatorConnection).filter(
            or_(
                CreatorConnection.requester_id == creator_id,
                CreatorConnection.receiver_id == creator_id
            ),
            CreatorConnection.status == "accepted"
        ).order_by(CreatorConnection.updated_at.desc()).all()

        results = [self._to_response(c) for c in conns]

        return CreatorConnectionsSummary(
            creator_id=creator_id,
            total_connections=len(results),
            connections=results
        )

    def get_pending_incoming_requests(self, db: Session, creator_id: int) -> list[ConnectionResponse]:
        conns = db.query(CreatorConnection).filter(
            CreatorConnection.receiver_id == creator_id,
            CreatorConnection.status == "pending"
        ).order_by(CreatorConnection.created_at.desc()).all()
        return [self._to_response(c) for c in conns]

    def get_pending_outgoing_requests(self, db: Session, creator_id: int) -> list[ConnectionResponse]:
        conns = db.query(CreatorConnection).filter(
            CreatorConnection.requester_id == creator_id,
            CreatorConnection.status == "pending"
        ).order_by(CreatorConnection.created_at.desc()).all()
        return [self._to_response(c) for c in conns]

    def check_connection_status(self, db: Session, creator_a_id: int, creator_b_id: int) -> str:
        if creator_a_id == creator_b_id:
            return "self"
        conn = db.query(CreatorConnection).filter(
            or_(
                and_(CreatorConnection.requester_id == creator_a_id, CreatorConnection.receiver_id == creator_b_id),
                and_(CreatorConnection.requester_id == creator_b_id, CreatorConnection.receiver_id == creator_a_id)
            )
        ).first()
        if not conn:
            return "none"
        if conn.status == "accepted":
            return "connected"
        if conn.status == "pending":
            return "pending_outgoing" if conn.requester_id == creator_a_id else "pending_incoming"
        return "rejected"

connection_service = ConnectionService()
