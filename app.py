# app.py
import os
from flask import Flask, redirect, url_for
import google.genai as genai

# Import the Blueprint
from viewer import view_bp
from keyword_tracker import ktracker_bp


def create_app():
    '''Flask アプリケーションを作成し

    Returns:
        Flask: Flask アプリケーションインスタンス
    '''
    # Generate Gemini API Client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    app.config['GENAI_CLIENT'] = client

    # Flassk アプリケーションの作成
    app = Flask(__name__)

    # トップページをビューにリダイレクト
    @app.route('/')
    def index():
        return redirect(url_for('view.view_page'))
    
    # Blueprint登録
    app.register_blueprint(view_bp, url_prefix='/view')
    app.register_blueprint(ktracker_bp, url_prefix='/ktracker')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)