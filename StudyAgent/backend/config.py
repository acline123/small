import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
DB_PATH = DATA_DIR / "study_agent.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", DEEPSEEK_API_KEY)
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "pptx"}

# 全网搜索（Bing 中国版 / DuckDuckGo，无需 API Key）
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
WEB_SEARCH_ENGINE = os.getenv("WEB_SEARCH_ENGINE", "auto").lower()
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVE_TOP_K = 4
MEMORY_LIMIT = 10

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"


def reload_env() -> None:
    """重新加载 .env，避免 Flask 热重载或修改 .env 后仍使用旧配置。"""
    global DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
    global EMBEDDING_API_KEY, EMBEDDING_BASE_URL, EMBEDDING_MODEL
    global FLASK_HOST, FLASK_PORT, FLASK_DEBUG, WEB_SEARCH_MAX_RESULTS, WEB_SEARCH_ENGINE

    load_dotenv(BASE_DIR / ".env", override=True)

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", DEEPSEEK_API_KEY)
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

    WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
    WEB_SEARCH_ENGINE = os.getenv("WEB_SEARCH_ENGINE", "auto").lower()
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"


def check_api_keys() -> list[str]:
    """检查必需的 API Key 是否已配置，返回缺失项说明。"""
    reload_env()
    missing = []
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sk-your-key-here":
        missing.append("DEEPSEEK_API_KEY（对话/摘要/意图识别）")
    if not EMBEDDING_API_KEY or EMBEDDING_API_KEY == "sk-your-key-here":
        missing.append("EMBEDDING_API_KEY（文档向量化，知识库构建必需）")
    return missing
