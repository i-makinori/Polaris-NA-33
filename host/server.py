# -*- coding: utf-8 -*-
from functools import reduce
#
import os
import sys
import yaml
from flask import Flask, Blueprint
# application
from models import db
from routes.portal_gate import PortalGate
from routes.post_gate import PostGate
from routes.faceman_gate import FacemanGate



# Config of PATH
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
config_file_path = os.path.join(base_dir, './config.yaml')


# Read Config
class YAMLParseError(Exception):
    """Custom Error for Parsing Configure File"""
    pass

def validate_config(conf):
    required_schema = {
        'database': {'path': str, 'track_modifications': bool},
        'server': {'port': int, 'debug': bool},
        'app_secret_key': str
    }

    for section, expected in required_schema.items():
        # 1. check if section exsits
        if section not in conf:
            raise ValueError(f"設定エラー: セクション '{section}' が見つかりません。")
        # 2. if the 'expected' is section, check contains
        if isinstance(expected, dict):
            for key, expected_type in expected.items():
                val = conf[section].get(key)
                if val is None:
                    raise ValueError(f"設定エラー: '{section}' 内にキー '{key}' がありません。")
                if not isinstance(val, expected_type):
                    raise TypeError(f"設定エラー: '{section}.{key}' は {expected_type.__name__} 型である必要があります。")
        # 3. otherwise, check its value.
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

    # Return
    return conf


# Init System
def init_database (conf, app):
    # Configure DB
    db_raw_path = conf['database']['path']
    db_path = os.path.join(base_dir, db_raw_path) if not os.path.isabs(db_raw_path) else db_raw_path
    db_modify = conf['database'].get('track_modifications', False)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_modify

    # Initialize DB
    db.init_app(app)

    # Return
    return None


def register_gate_to_app(app, name, GateClass, config, db_session, template_dir):
    """
    Instantiate a Gate class and register its Blueprint to the Flask application.
    This factory function encapsulates the entire setup process for each Gate.
    """

    # 1. Initialize Blueprint with the specified name and template directory.
    bp = Blueprint(name, __name__, template_folder=template_dir)

    # 2. Instantiate the Gate class by invoking its constructor with config and session.
    ctrl = GateClass(config=config, db_session=db_session)

    # 3. Register Blueprint to ctrl
    ctrl.register(bp)

    # 4. Register the configured Blueprint to the main Flask application.
    app.register_blueprint(bp)

    # Return
    return app, ctrl


def create_app():
    # Read config file
    conf = read_config(config_file_path)

    # Init APP
    assets_folder = os.path.join(base_dir, './host/static/')

    app = Flask(__name__, static_folder=assets_folder)
    app.secret_key = conf.get('app_secret_key')

    # Init DataBase
    init_database(conf, app)

    # Config template dir
    template_dir = os.path.join(base_dir, './host/templates/')
    app.template_folder = template_dir

    # Register gates to app

    # 1. Gate definitions as [('name', Constructor)]
    gate_definitions = [('portal',   PortalGate),
                        ('posts',    PostGate),
                        ('facemans', FacemanGate),]

    # 2. Functional Reduction without 'def'
    # We use a lambda to process each registration and return the updated app.
    app = reduce(lambda acc_app, gate_def:
                 register_gate_to_app(acc_app, gate_def[0], gate_def[1], conf, db.session, template_dir)[0],
                 gate_definitions,
                 app)

    # Return
    return app, conf


# main
if __name__ == '__main__':
    app,  conf = create_app()

    with app.app_context():
        db.create_all()


    port = conf['server'].get('port', 5050)
    debug = conf['server'].get('debug', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
