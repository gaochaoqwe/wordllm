from app.utils.logger import logger

def register_websocket_handlers(socketio):
    """注册WebSocket处理程序"""
    from app.websocket.handlers import setup_handlers
    setup_handlers(socketio)
    logger.info("WebSocket handlers registered")
