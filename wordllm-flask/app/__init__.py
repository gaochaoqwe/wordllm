from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler
import os

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # 加载配置
    if config_class is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_object(config_class)
    
    # 确保必要的目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['STORAGE_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGIN'], supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGIN'], ping_interval=app.config['WS_HEARTBEAT_INTERVAL']//1000)
    
    # 设置日志
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/wordllm.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('WordLLM startup')
    
    # 注册蓝图
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册错误处理
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # 注册WebSocket处理
    from app.websocket import register_websocket_handlers
    register_websocket_handlers(socketio)
    
    @app.route('/')
    def index():
        return {'status': 'WordLLM API is running'}
    
    return app
