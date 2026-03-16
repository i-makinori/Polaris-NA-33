# -*- coding: utf-8 -*-
import os
import sys
import yaml
from flask import Flask, Blueprint
# application
from models import db
from routes.post_controller import PostController



def create_app():
    app = Flask(__name__)

    # パス設定
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
    config_path = os.path.join(base_dir, './config.yaml')
    app.template_folder = os.path.join(base_dir, './host/templates/')

    # Config読み込み
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
    except Exception as e:
        print(f"Config Error: {e}")
        sys.exit(1)

    # DB設定
    db_raw_path = conf['database']['path']
    db_path = os.path.join(base_dir, db_raw_path) if not os.path.isabs(db_raw_path) else db_raw_path

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = conf['database'].get('track_modifications', False)

    # DB初期化
    db.init_app(app)

    # Controller & Blueprint
    posts_bp = Blueprint('posts', __name__)
    # db.session を注入
    post_ctrl = PostController(config=conf, db_session=db.session)
    post_ctrl.register(posts_bp)

    app.register_blueprint(posts_bp)

    return app, conf


if __name__ == '__main__':
    app,  conf = create_app()

    with app.app_context():
        db.create_all()

    port = conf['server'].get('port', 5050)
    debug = conf['server'].get('debug', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
