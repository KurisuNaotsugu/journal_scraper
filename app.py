# app.py
import os
from flask import Flask, redirect, url_for
import google.genai as genai

# Import the Blueprint
from viewer import viewer_bp
from manual_search import manualsearch_bp
from keyword_tracker import ktracker_bp
from howto import howto_bp

def create_app():
    '''Flask アプリケーションを作成し

    Returns:
        Flask: Flask アプリケーションインスタンス
    '''

    # Flassk アプリケーションの作成
    app = Flask(__name__)

    # Generate Gemini API Client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    app.config['GENAI_CLIENT'] = client

    # トップページをビューにリダイレクト
    @app.route('/')
    def index():
        return redirect(url_for('viewer.view_page'))
    
    # Blueprint登録
    app.register_blueprint(viewer_bp, url_prefix='/viewer')
    app.register_blueprint(manualsearch_bp, url_prefix='/manualsearch')
    app.register_blueprint(ktracker_bp, url_prefix='/ktracker')
    app.register_blueprint(howto_bp, url_prefix='/howto')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)