from openai import OpenAI

import config


def get_client() -> OpenAI:
    return OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    """调用 DeepSeek Chat API。"""
    client = get_client()
    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        stream=False,
    )
    return response.choices[0].message.content or ""
