from langchain_openai import OpenAIEmbeddings

import config


def get_embeddings() -> OpenAIEmbeddings:
    """
    Embedding 封装（OpenAI 兼容接口，默认 SiliconFlow BAAI/bge-m3）。
    """
    if not config.EMBEDDING_API_KEY:
        raise ValueError(
            "未配置 EMBEDDING_API_KEY。请在 backend/.env 中填入 Embedding API Key，"
            "可从 https://siliconflow.cn 注册获取。"
        )
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        api_key=config.EMBEDDING_API_KEY,
        base_url=config.EMBEDDING_BASE_URL,
        check_embedding_ctx_length=False,
    )
