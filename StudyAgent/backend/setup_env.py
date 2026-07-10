"""交互式配置 backend/.env 中的 API Key。"""

from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"
EXAMPLE_PATH = Path(__file__).resolve().parent / ".env.example"


def read_existing() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_PATH.exists():
        return values
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def prompt_key(name: str, hint: str, current: str) -> str:
    placeholder = "sk-your-key-here"
    if current and current != placeholder:
        masked = current[:8] + "..." + current[-4:] if len(current) > 12 else current
        print(f"  当前已配置: {masked}")
        choice = input("  保留当前值? [Y/n]: ").strip().lower()
        if choice in ("", "y", "yes"):
            return current

    print(f"  {hint}")
    value = input(f"  请输入 {name}: ").strip()
    while not value or value == placeholder:
        print("  Key 不能为空，也不能是占位符 sk-your-key-here")
        value = input(f"  请输入 {name}: ").strip()
    return value


def main() -> None:
    if not ENV_PATH.exists():
        ENV_PATH.write_text(EXAMPLE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"已从模板创建 {ENV_PATH}\n")

    existing = read_existing()
    print("StudyAgent 后端 API Key 配置\n")

    deepseek = prompt_key(
        "DEEPSEEK_API_KEY",
        "对话/摘要/意图识别（老师提供的 token-cloud Key 或 DeepSeek 官方 Key）",
        existing.get("DEEPSEEK_API_KEY", ""),
    )
    embedding = prompt_key(
        "EMBEDDING_API_KEY",
        "文档向量化（SiliconFlow 注册: https://siliconflow.cn）",
        existing.get("EMBEDDING_API_KEY", ""),
    )

    content = EXAMPLE_PATH.read_text(encoding="utf-8")
    for key, value in {
        "DEEPSEEK_API_KEY": deepseek,
        "EMBEDDING_API_KEY": embedding,
    }.items():
        lines = []
        replaced = False
        for line in content.splitlines():
            if line.startswith(f"{key}="):
                lines.append(f"{key}={value}")
                replaced = True
            else:
                lines.append(line)
        if not replaced:
            lines.append(f"{key}={value}")
        content = "\n".join(lines) + "\n"

    ENV_PATH.write_text(content, encoding="utf-8")
    print(f"\n配置已保存到 {ENV_PATH}")
    print("请重启后端: python run.py")


if __name__ == "__main__":
    main()
