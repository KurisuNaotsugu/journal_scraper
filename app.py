# app.py
import os
from flask import Flask, render_template
import google.genai as genai
import secrets
from datetime import date

from db.init_db import init_db

# Import the Blueprint
from blueprints.viewer import viewer_bp
from blueprints.manual_search import manualsearch_bp
from blueprints.keyword_tracker import ktracker_bp
from blueprints.settings import settings_bp
from blueprints.howto import howto_bp

def create_app():
    '''Flask アプリケーションの作成'''

    # アプリケーションインスタンスの作成
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    # DB初期化

    with app.app_context():
        today = date.today().strftime("%Y-%m-%d")
        init_db(init_date=today)

    # Generate Gemini API Client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    app.config['GENAI_CLIENT'] = client

    # トップページをビューにリダイレクト
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Blueprint登録
    app.register_blueprint(viewer_bp, url_prefix='/viewer')
    app.register_blueprint(manualsearch_bp, url_prefix='/manualsearch')
    app.register_blueprint(ktracker_bp, url_prefix='/ktracker')
    app.register_blueprint(howto_bp, url_prefix='/howto')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)