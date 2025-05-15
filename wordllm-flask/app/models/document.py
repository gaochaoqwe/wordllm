from datetime import datetime
from app import db

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=1)  # 1=unwritten, 2=writing, 3=completed
    file_path = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    original_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 添加自定义提示词字段
    outline_prompt = db.Column(db.Text, nullable=True, comment='一级、二级、三级目录生成的自定义提示词')
    subchapter_prompt = db.Column(db.Text, nullable=True, comment='后续级别目录生成的自定义提示词')
    content_prompt = db.Column(db.Text, nullable=True, comment='文档内容生成的自定义提示词')
    
    # 模板相关字段已移除
    
    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'status_text': self.get_status_text(),
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'original_filename': self.original_filename,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'outline_prompt': self.outline_prompt,
            'subchapter_prompt': self.subchapter_prompt,
            'content_prompt': self.content_prompt
        }
        
        # 添加预览和下载URL
        if self.file_path:
            data['preview_url'] = f'/api/templates/{self.id}/preview'
            data['download_url'] = f'/api/templates/{self.id}/download'
            data['file_url'] = f'/api/templates/{self.id}/preview'
            
        return data
    
    def get_status_text(self):
        status_map = {
            1: 'unwritten',
            2: 'writing',
            3: 'completed'
        }
        return status_map.get(self.status, 'unknown')
