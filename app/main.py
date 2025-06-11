from flask import Flask, g
from app.routes.recommend import recommend_bp
from app.core.database import SessionLocal

def create_app():
    app = Flask(__name__)
    app.register_blueprint(recommend_bp)
    
    # 요청 전에 세션 생성
    @app.before_request
    def create_session():
        g.db = SessionLocal()

    # 요청 후 세션 정리
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    print("📌 Registered Routes:")  
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:25s} {rule.methods} {rule.rule}")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
