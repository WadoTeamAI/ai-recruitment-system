"""
AI採用支援システム - WSGI エントリーポイント
本番環境でのアプリケーション起動用
"""

from app import app
from config import config
import os

# 環境設定
config_name = os.environ.get('FLASK_ENV', 'production')
app.config.from_object(config[config_name])

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
