from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

def create_app():
    """创建Flask应用实例"""
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'jiangsu-tourism-rag-system')
    
    # 设置JSON支持UTF-8编码
    app.config['JSON_AS_ASCII'] = False
    
    # 启用CORS，添加更完整的配置
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)