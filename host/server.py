# -*- coding: utf-8 -*-
import os
import sys
import yaml
from flask import Flask, Blueprint
# application
from models import db
from routes.post_controller import PostController
from routes.user_controller import UserController


# Config of PATH
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
config_file_path = os.path.join(base_dir, './config.yaml')


# Read Config
class YAMLParseError(Exception):
    """設定ファイルに関するカスタムエラー"""
    pass

def validate_config(conf):
    # 必須構造の定義: {セクション: {キー: 型}}
    required_schema = {
        'database': {'path': str, 'track_modifications': bool},
        'server': {'port': int, 'debug': bool}
    }
    for section, keys in required_schema.items():
        if section not in conf:
            raise YAMLParseError(f"セクション '{section}' が config.yaml に存在しません。")
        for key, expected_type in keys.items():
            if key not in conf[section]:
                raise YAMLParseError(f"設定項目 '{section}.{key}' が定義されていません。")
            # 型チェックを追加してさらなる厳密さを確保
            if not isinstance(conf[section][key], expected_type):
                raise YAMLParseError(
                    f"設定項目 '{section}.{key}' の型が正しくありません。"
                    f"（期待値: {expected_type.__name__}, 実数値: {type(conf[section][key]).__name__}）"
                )
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

    # init DataBase
    init_database(conf, app)
    
    # config template dir
    template_dir = os.path.join(base_dir, './host/templates/')
    app.template_folder = template_dir

    # --- PostController ---
    posts_bp = Blueprint('posts', __name__, template_folder=template_dir)
    post_ctrl = PostController(config=conf, db_session=db.session)
    post_ctrl.register(posts_bp)
    app.register_blueprint(posts_bp)

    # --- serController ---
    user_bp = Blueprint('users', __name__, template_folder=template_dir)
    user_ctrl = UserController(db_session=db.session)
    user_ctrl.register(user_bp)
    app.register_blueprint(user_bp)


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
