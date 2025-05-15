import logging
import os
from logging.handlers import RotatingFileHandler

# 创建日志目录
if not os.path.exists('logs'):
    os.makedirs('logs', exist_ok=True)

# 配置日志格式
formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')

# 创建文件处理器
file_handler = RotatingFileHandler(
    'logs/wordllm.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# 创建和配置logger
logger = logging.getLogger('wordllm')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 关闭在导入时的传播
logger.propagate = False
