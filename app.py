# app.py
import os
from flask import Flask, redirect, url_for
import google.genai as genai

# Import the Blueprint
from viewer import view_bp
from keywords import keywords_bp


def create_app():
    '''Flask アプリケーションを作成し、Blueprint を登録する関数
    - topページを /main にリダイレクト
    - Gemini API クライアントを作成し、アプリケーション設定に保存
    
    Returns:
        Flask: Flask アプリケーションインスタンス
    '''
    app = Flask(__name__)

    # Redirect the top page to /main
    @app.route('/')
    def index():
        return redirect(url_for('view.view_page'))
    
    # Generate Gemini API Client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    app.config['GENAI_CLIENT'] = client
    
    # Register Blueprint
    app.register_blueprint(view_bp, url_prefix='/view')
    app.register_blueprint(keywords_bp, url_prefix='/keywords')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)