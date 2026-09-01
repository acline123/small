from openai import OpenAI

import config

_client = None
_client_config = None


def get_client() -> OpenAI:
    """惰性单例 client，key/base_url 变化时自动重建。"""
    global _client, _client_config
    cfg = (config.DEEPSEEK_API_KEY, config.DEEPSEEK_BASE_URL)
    if _client is None or _client_config != cfg:
        _client = OpenAI(api_key=cfg[0], base_url=cfg[1])
        _client_config = cfg
    return _client


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    """调用 DeepSeek Chat API（非流式）。"""
    client = get_client()
    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        stream=False,
    )
    return response.choices[0].message.content or ""


def chat_stream(messages: list[dict], temperature: float = 0.7):
    """流式调用 DeepSeek Chat API，逐段产出文本。"""
    client = get_client()
    stream = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
