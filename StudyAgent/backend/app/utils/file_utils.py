import uuid

import config


def _normalize_filename(filename: str) -> str:
    return (filename or "").replace("\\", "/").split("/")[-1].strip()


def allowed_file(filename: str) -> bool:
    filename = _normalize_filename(filename)
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    filename = _normalize_filename(filename)
    if "." not in filename:
        return "txt"
    return filename.rsplit(".", 1)[1].lower()


def save_upload_file(file_storage) -> tuple[str, str, int]:
    """保存上传文件，返回 (原始文件名, 完整路径, 文件大小)。"""
    original = _normalize_filename(file_storage.filename)
    if not original:
        original = f"upload_{uuid.uuid4().hex[:8]}.txt"

    ext = f".{get_file_type(original)}"
    storage_name = f"{uuid.uuid4().hex}{ext}"
    save_path = config.UPLOAD_DIR / storage_name
    file_storage.save(str(save_path))
    file_size = save_path.stat().st_size
    return original, str(save_path), file_size
