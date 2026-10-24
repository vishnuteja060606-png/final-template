import os
import re
import uuid
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.config import settings

class FileService:
    def __init__(self, base_upload_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_upload_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal and remove dangerous characters."""
        # Strip path info
        clean_name = os.path.basename(filename)
        # Remove any non-alphanumeric except dots, dashes, underscores
        clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", clean_name)
        # Prevent multiple dots or leading dots
        clean_name = re.sub(r"\.+", ".", clean_name).strip(".")
        return clean_name or "uploaded_file"

    def get_extension(self, filename: str) -> str:
        clean = self.sanitize_filename(filename)
        if "." in clean:
            return clean.rsplit(".", 1)[1].lower()
        return ""

    def validate_file(self, file: UploadFile) -> None:
        """Validate file size and extension."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must have a filename."
            )
        
        ext = self.get_extension(file.filename)
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '.{ext}' is not allowed. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

    async def save_creator_file(self, file: UploadFile, creator_id: int) -> tuple[str, str, int, str]:
        """
        Saves an uploaded file to a creator-specific directory.
        Returns: (relative_storage_path, original_filename, file_size, mime_type)
        """
        self.validate_file(file)

        creator_dir = self.base_dir / "creators" / str(creator_id)
        creator_dir.mkdir(parents=True, exist_ok=True)

        original_clean = self.sanitize_filename(file.filename)
        ext = self.get_extension(file.filename)
        unique_name = f"{uuid.uuid4().hex[:12]}_{original_clean}"
        target_path = creator_dir / unique_name

        # Ensure no path traversal escapes creator directory
        if not str(target_path.resolve()).startswith(str(creator_dir.resolve())):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path detected."
            )

        # Stream copy to check size limit while saving
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        size = 0

        try:
            async with aiofiles.open(target_path, "wb") as out_file:
                while content := await file.read(1024 * 1024):  # 1MB chunks
                    size += len(content)
                    if size > max_bytes:
                        # Clean up partial file
                        target_path.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                        )
                    await out_file.write(content)
        except Exception as e:
            if target_path.exists():
                target_path.unlink(missing_ok=True)
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )

        # Store relative web-safe path
        rel_path = f"/uploads/creators/{creator_id}/{unique_name}"
        mime_type = file.content_type or "application/octet-stream"

        return rel_path, original_clean, size, mime_type

    def delete_file(self, relative_path: str) -> bool:
        """Safely delete a file given its relative web path."""
        try:
            # Strip leading '/uploads/'
            clean_rel = relative_path.lstrip("/").replace("uploads/", "", 1)
            full_path = (self.base_dir / clean_rel).resolve()
            # Security check: must reside inside base_dir
            if str(full_path).startswith(str(self.base_dir)):
                if full_path.exists() and full_path.is_file():
                    full_path.unlink()
                    return True
        except Exception:
            pass
        return False

file_service = FileService()
