from flask import Flask
from app.routes.recommend import recommend_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(recommend_bp)
    
    
    print("📌 Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:25s} {rule.methods} {rule.rule}")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
