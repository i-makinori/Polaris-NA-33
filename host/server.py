# -*- coding: utf-8 -*-
import os
import sys
import yaml
from flask import Flask, Blueprint
from routes.post_controller import PostController

# 基準となるディレクトリ（server.pyのある場所）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config():
    # config.yaml は server.py の一つ上の階層にある
    config_path = os.path.join(BASE_DIR, "../config.yaml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
            
            # --- パスの正規化 (Lisp的な柔軟性をPythonで) ---
            db_path = conf['database']['path']
            if not os.path.isabs(db_path):
                # 相対パスなら、server.pyの場所を基準に絶対パス化
                conf['database']['path'] = os.path.abspath(os.path.join(BASE_DIR, db_path))
            
            return conf
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error: Config load failed.\nDetail: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    conf_data = load_config()

    app = Flask(__name__)

    # YAMLからサーバー設定を読み取って適用
    server_conf = conf_data.get('server', {})
    debug_mode = server_conf.get('debug', True)
    port_num = server_conf.get('port', 5050)

    # コントローラー初期化 (configの木を渡す)
    # db_sessionは、このあと conf_data['database']['path'] を使って接続を作る
    post_ctrl = PostController(config=conf_data, db_session=None)

    # Blueprint登録
    posts_bp = Blueprint('posts', __name__, url_prefix='/posts')
    post_ctrl.register(posts_bp)
    app.register_blueprint(posts_bp)

    print(f"Database Path: {conf_data['database']['path']}")
    app.run(host='0.0.0.0', port=port_num, debug=debug_mode)


