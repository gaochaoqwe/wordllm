import os
from app import create_app, socketio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # 使用socketio运行应用，而不是app.run()
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=app.config['DEBUG']
    )
