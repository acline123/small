from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader


def load_document(file_path: str, file_type: str):
    """根据文件类型加载文档。"""
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    elif file_type == "docx":
        loader = Docx2txtLoader(file_path)
    elif file_type == "txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")
    return loader.load()
