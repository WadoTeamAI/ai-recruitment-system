"""
AI採用支援システム - 設定管理
環境変数とデフォルト設定
"""

import os

class Config:
    """アプリケーション設定クラス"""
    
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hr_system_secret_key_2024'
    
    # アプリケーション設定
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # アップロード設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 企業設定（環境変数で上書き可能）
    COMPANY_NAME = os.environ.get('COMPANY_NAME', '株式会社テックイノベーション')
    COMPANY_MISSION = os.environ.get('COMPANY_MISSION', 'テクノロジーで社会課題を解決し、持続可能な未来を創造する')
    
    @staticmethod
    def init_app(app):
        """アプリケーション初期化"""
        pass

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    
class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 本番環境用の追加設定
        import logging
        from logging import StreamHandler
        
        # ログレベル設定
        if not app.debug:
            app.logger.setLevel(logging.INFO)
            
            # ストリームハンドラー追加
            stream_handler = StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
