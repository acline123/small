import config
from app import create_app

app = create_app()

if __name__ == "__main__":
    missing = config.check_api_keys()
    if missing:
        print("⚠️  警告：以下 API Key 未配置：")
        for item in missing:
            print(f"   - {item}")
        print("   请复制 backend/.env.example 为 backend/.env 并填入密钥后重启\n")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
