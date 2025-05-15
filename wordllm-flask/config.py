import os
import json
from datetime import timedelta

# 加载config.json文件
def load_json_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取config.json配置文件失败: {str(e)}")
        return {}
        
# 加载配置
config_data = load_json_config()

class Config:
    # Flask配置
    SECRET_KEY = config_data.get('flask', {}).get('SECRET_KEY', 'dev-secret-key')
    DEBUG = config_data.get('flask', {}).get('DEBUG', True)
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = config_data.get('database', {}).get('DATABASE_URI', 'sqlite:///wordllm.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = config_data.get('jwt', {}).get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=config_data.get('jwt', {}).get('JWT_ACCESS_TOKEN_EXPIRES', 1))
    
    # 文件上传配置
    UPLOAD_FOLDER = config_data.get('file_upload', {}).get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
    STORAGE_FOLDER = config_data.get('file_upload', {}).get('STORAGE_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage'))
    MAX_CONTENT_LENGTH = config_data.get('file_upload', {}).get('MAX_CONTENT_LENGTH', 16) * 1024 * 1024  # 默认16MB
    
    # OpenAI配置 - 特别注意这里
    OPENAI_API_KEY = config_data.get('openai', {}).get('OPENAI_API_KEY')
    OPENAI_MODEL_NAME = config_data.get('openai', {}).get('OPENAI_MODEL_NAME')
    OPENAI_API_BASE = config_data.get('openai', {}).get('OPENAI_API_BASE')
    
    # 速率限制配置
    RATE_LIMIT_WINDOW_MS = config_data.get('rate_limit', {}).get('RATE_LIMIT_WINDOW_MS', 900000)  # 15分钟
    RATE_LIMIT_MAX_REQUESTS = config_data.get('rate_limit', {}).get('RATE_LIMIT_MAX_REQUESTS', 100)
    
    # CORS配置
    CORS_ORIGIN = config_data.get('cors', {}).get('CORS_ORIGIN', 'http://localhost:5174')
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL = config_data.get('websocket', {}).get('WS_HEARTBEAT_INTERVAL', 30000)  # 30秒
