from langchain_openai import OpenAIEmbeddings

import config


def get_embeddings() -> OpenAIEmbeddings:
    """
    DeepSeek Embedding 封装。
    DeepSeek 官方 API 暂不提供 Embedding 端点，此处使用 OpenAI 兼容 Embedding 服务。
    可在 .env 中配置 EMBEDDING_BASE_URL 和 EMBEDDING_MODEL。
    """
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        openai_api_key=config.EMBEDDING_API_KEY,
        openai_api_base=config.EMBEDDING_BASE_URL,
        check_embedding_ctx_length=False,
    )
