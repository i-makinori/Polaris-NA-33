# -*- coding: utf-8 -*-
import os
import sys
import yaml
from flask import Flask, Blueprint
# application
from models import db
from routes.post_gate import PostGate
from routes.faceman_gate import FacemanGate


# Config of PATH
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
config_file_path = os.path.join(base_dir, './config.yaml')


# Read Config
class YAMLParseError(Exception):
    """設定ファイルに関するカスタムエラー"""
    pass

def validate_config(conf):
    required_schema = {
        'database': {'path': str, 'track_modifications': bool},
        'server': {'port': int, 'debug': bool},
        'app_secret_key': str
    }

    for section, expected in required_schema.items():
        # 1. セクションの存在チェック
        if section not in conf:
            raise ValueError(f"設定エラー: セクション '{section}' が見つかりません。")
        # 2. 値が辞書（セクション）の場合、その中身をチェック
        if isinstance(expected, dict):
            for key, expected_type in expected.items():
                val = conf[section].get(key)
                if val is None:
                    raise ValueError(f"設定エラー: '{section}' 内にキー '{key}' がありません。")
                if not isinstance(val, expected_type):
                    raise TypeError(f"設定エラー: '{section}.{key}' は {expected_type.__name__} 型である必要があります。")
        # 3. 直値（app_secret_keyなど）の場合のチェック
        else:
            if not isinstance(conf[section], expected):
                raise TypeError(f"設定エラー: '{section}' は {expected.__name__} 型である必要があります。")
    return True

def read_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
    except Exception as e:
        print(f"Config Error: {e}")
        sys.exit(1)

    validate_config(conf)

    # return
    return conf


# Init System
def init_database (conf, app):
    # DB設定
    db_raw_path = conf['database']['path']
    db_path = os.path.join(base_dir, db_raw_path) if not os.path.isabs(db_raw_path) else db_raw_path
    db_modify = conf['database'].get('track_modifications', False)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_modify

    # DB初期化
    db.init_app(app)

    # return
    return None


def create_app():
    # read config file
    conf = read_config(config_file_path)

    # init APP
    assets_folder = os.path.join(base_dir, './host/static/')
    
    app = Flask(__name__, static_folder=assets_folder)
    app.secret_key = conf.get('app_secret_key')

    # init DataBase
    init_database(conf, app)
    
    # config template dir
    template_dir = os.path.join(base_dir, './host/templates/')
    app.template_folder = template_dir

    # --- PostGate ---
    posts_bp = Blueprint('posts', __name__, template_folder=template_dir)
    post_ctrl = PostGate(config=conf, db_session=db.session)
    post_ctrl.register(posts_bp)
    app.register_blueprint(posts_bp)

    # --- facemanGate ---
    faceman_bp = Blueprint('facemans', __name__, template_folder=template_dir)
    faceman_ctrl = FacemanGate(db_session=db.session)
    faceman_ctrl.register(faceman_bp)
    app.register_blueprint(faceman_bp)


    # return
    return app, conf


# main
if __name__ == '__main__':
    app,  conf = create_app()

    with app.app_context():
        db.create_all()


    port = conf['server'].get('port', 5050)
    debug = conf['server'].get('debug', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
