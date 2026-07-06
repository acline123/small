import uuid
from datetime import datetime

from werkzeug.utils import secure_filename

import config


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower()


def save_upload_file(file_storage) -> tuple[str, str, int]:
    """保存上传文件，返回 (安全文件名, 完整路径, 文件大小)。"""
    filename = secure_filename(file_storage.filename)
    if not filename:
        filename = f"upload_{uuid.uuid4().hex[:8]}.txt"
    save_path = config.UPLOAD_DIR / filename
    file_storage.save(str(save_path))
    file_size = save_path.stat().st_size
    return filename, str(save_path), file_size
