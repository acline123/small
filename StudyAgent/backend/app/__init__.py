from flask import Flask
from flask_cors import CORS

from app.models.database import init_db
from app.routes.chat import chat_bp
from app.routes.document import document_bp
from app.routes.exercise import exercise_bp
from app.routes.graph import graph_bp
from app.routes.history import history_bp
from app.routes.summary import summary_bp
from app.routes.upload import upload_bp


def create_app():
    flask_app = Flask(__name__)
    CORS(flask_app)

    init_db()

    # 注册 MCP Tools
    import app.tools  # noqa: F401

    flask_app.register_blueprint(upload_bp, url_prefix="/api")
    flask_app.register_blueprint(document_bp, url_prefix="/api")
    flask_app.register_blueprint(chat_bp, url_prefix="/api")
    flask_app.register_blueprint(summary_bp, url_prefix="/api")
    flask_app.register_blueprint(history_bp, url_prefix="/api")
    flask_app.register_blueprint(graph_bp, url_prefix="/api")
    flask_app.register_blueprint(exercise_bp, url_prefix="/api")

    @flask_app.route("/api/health")
    def health():
        return {"status": "ok"}

    return flask_app
