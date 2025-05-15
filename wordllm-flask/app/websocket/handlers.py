from flask_socketio import emit, join_room, leave_room, Namespace
from app.utils.logger import logger

def setup_handlers(socketio):
    """设置WebSocket处理器"""
    
    @socketio.on('connect', namespace='/ws')
    def handle_connect():
        """处理连接事件"""
        logger.info("Client connected to WebSocket")
        emit('status', {'status': 'connected'})
    
    @socketio.on('disconnect', namespace='/ws')
    def handle_disconnect():
        """处理断开连接事件"""
        logger.info("Client disconnected from WebSocket")
    
    @socketio.on('subscribe', namespace='/ws')
    def handle_subscribe(data):
        """处理订阅事件"""
        if 'topic' not in data:
            emit('error', {'error': 'Topic is required'})
            return
        
        topic = data['topic']
        # 将客户端加入指定主题的房间
        join_room(topic)
        logger.info(f"Client subscribed to topic: {topic}")
        emit('status', {'status': 'subscribed', 'topic': topic})
    
    @socketio.on('unsubscribe', namespace='/ws')
    def handle_unsubscribe(data):
        """处理取消订阅事件"""
        if 'topic' not in data:
            emit('error', {'error': 'Topic is required'})
            return
        
        topic = data['topic']
        # 将客户端从指定主题的房间移除
        leave_room(topic)
        logger.info(f"Client unsubscribed from topic: {topic}")
        emit('status', {'status': 'unsubscribed', 'topic': topic})
    
    # 为AI生成创建专用命名空间
    class GenerateNamespace(Namespace):
        def on_connect(self):
            """处理连接事件"""
            session_id = self.namespace.split('/')[-1]
            logger.info(f"Client connected to generation for session: {session_id}")
            emit('status', {'status': 'connected', 'sessionId': session_id})
        
        def on_disconnect(self):
            """处理断开连接事件"""
            session_id = self.namespace.split('/')[-1]
            logger.info(f"Client disconnected from generation for session: {session_id}")
    
    # 注册AI生成命名空间
    socketio.on_namespace(GenerateNamespace('/ws/generate'))
    
    # 实时文档协作命名空间
    class DocumentNamespace(Namespace):
        def on_connect(self):
            """处理连接事件"""
            logger.info("Client connected to document collaboration")
            emit('status', {'status': 'connected'})
        
        def on_disconnect(self):
            """处理断开连接事件"""
            logger.info("Client disconnected from document collaboration")
        
        def on_join(self, data):
            """加入文档协作会话"""
            if 'documentId' not in data:
                emit('error', {'error': 'Document ID is required'})
                return
            
            document_id = data['documentId']
            room = f"document_{document_id}"
            join_room(room)
            logger.info(f"Client joined document room: {room}")
            emit('status', {'status': 'joined', 'documentId': document_id})
        
        def on_leave(self, data):
            """离开文档协作会话"""
            if 'documentId' not in data:
                emit('error', {'error': 'Document ID is required'})
                return
            
            document_id = data['documentId']
            room = f"document_{document_id}"
            leave_room(room)
            logger.info(f"Client left document room: {room}")
            emit('status', {'status': 'left', 'documentId': document_id})
        
        def on_update(self, data):
            """处理文档更新事件"""
            if 'documentId' not in data or 'content' not in data:
                emit('error', {'error': 'Document ID and content are required'})
                return
            
            document_id = data['documentId']
            content = data['content']
            user_id = data.get('userId', 'anonymous')
            
            # 广播更新消息到所有在此文档房间的客户端（除了发送者）
            room = f"document_{document_id}"
            emit('document_update', {
                'documentId': document_id,
                'content': content,
                'userId': user_id,
                'timestamp': data.get('timestamp')
            }, room=room, include_self=False)
            
            logger.info(f"Document update broadcast: {document_id}")
    
    # 注册文档协作命名空间
    socketio.on_namespace(DocumentNamespace('/ws/document'))
