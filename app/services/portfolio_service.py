from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.portfolio import PortfolioItem
from app.schemas.portfolio import PortfolioItemCreate, PortfolioItemUpdate
from app.services.file_service import file_service
from app.services.creator_service import creator_service

class PortfolioService:
    @staticmethod
    def get_by_id(db: Session, item_id: int) -> PortfolioItem | None:
        return db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()

    @staticmethod
    def list_by_creator(db: Session, creator_id: int) -> list[PortfolioItem]:
        return db.query(PortfolioItem).filter(
            PortfolioItem.creator_id == creator_id
        ).order_by(PortfolioItem.is_pinned.desc(), PortfolioItem.created_at.desc()).all()

    @staticmethod
    async def create_item(
        db: Session, creator_id: int, file: UploadFile, metadata: PortfolioItemCreate
    ) -> PortfolioItem:
        # Save file to storage
        rel_path, orig_filename, file_size, mime_type = await file_service.save_creator_file(file, creator_id)

        # Detect format from extension if not provided
        ext = file_service.get_extension(orig_filename).upper()
        detected_format = metadata.format or ext

        item = PortfolioItem(
            creator_id=creator_id,
            title=metadata.title,
            description=metadata.description,
            file_path=rel_path,
            original_filename=orig_filename,
            mime_type=mime_type,
            file_size=file_size,
            content_type=metadata.content_type,
            aspect_ratio=metadata.aspect_ratio,
            format=detected_format,
            tools_models=metadata.tools_models,
            skills=metadata.skills,
            specialization=metadata.specialization,
            tags=metadata.tags,
            workflow=metadata.workflow,
            is_pinned=False,
            pin_order=0,
            views_count=0
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        # Enforce mandatory 2 uploads publication status
        creator_service.refresh_publication_status(db, creator_id)
        return item

    @staticmethod
    def update_item(db: Session, item: PortfolioItem, data: PortfolioItemUpdate) -> PortfolioItem:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_item(db: Session, item: PortfolioItem) -> None:
        creator_id = item.creator_id
        # First remove physical file
        if item.file_path:
            file_service.delete_file(item.file_path)
        # Then remove DB record
        db.delete(item)
        db.commit()
        # Enforce mandatory 2 uploads publication status
        creator_service.refresh_publication_status(db, creator_id)

    @staticmethod
    def increment_view(db: Session, item_id: int) -> int:
        item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
        if item:
            item.views_count = (item.views_count or 0) + 1
            db.commit()
            return item.views_count
        return 0

portfolio_service = PortfolioService()
