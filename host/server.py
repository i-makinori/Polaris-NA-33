# -*- coding: utf-8 -*-
from functools import reduce
#
import os
import sys
from flask import Flask, Blueprint
import logging
from logging.handlers import RotatingFileHandler
# application
from read_config import read_config_yaml
from models import db
from routes.portal_gate import PortalGate
from routes.faceman_gate import FacemanGate
from routes.tolopica_gate import TolopicaGate
from routes.ranference_gate import RanferenceGate


# Configs
config_YAML_required_schemas = {
    'database': {'path': str, 'track_modifications': bool},
    'logger': {'path': str, 'log_level': str},
    'server': {'port': int, 'debug': bool},
    'app_secret_key': str
}


## path configs
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
config_file_path = os.path.join(base_dir, './config.yaml')
assets_folder = os.path.join(base_dir, './host/static/')
template_dir = os.path.join(base_dir, './host/templates/')


# Init System

def make_path_dir_if_not_exists(pathname):
    dirname = os.path.dirname(pathname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    

def init_database (app, conf):
    # 0. Parse conf
    # 0.1 path
    db_raw_path = conf['database']['path']
    db_path = os.path.join(base_dir, db_raw_path) if not os.path.isabs(db_raw_path) else db_raw_path
    # 0.2... modify, ...
    db_modify = conf['database']['track_modifications']

    # 1. Configure DB
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_modify

    # 2. Initialize DB
    if db_path:
        make_path_dir_if_not_exists(db_path)
    db.init_app(app)

    # R. Return
    return app




def is_log_level_exists_in_logging_p__otherwise__errror_and_exit (level_str):
    # 2. logging に その LogLevel が存在するかをチェック (logging._nameToLevel を直接参照)
    if level_str not in logging._nameToLevel:
        # 無ければエラー出力
        sys.stderr.write(f"Invalid log_level: '{level_str}'\n")
        sys.stderr.write("Available levels:\n")

        # 数値順にソートして「名前:数値」の形式で出力
        for name, val in sorted(logging._nameToLevel.items(), key=lambda x: x[1]):
            if name != "NOTSET":
                sys.stderr.write(f"  {name} : {val}\n")
        sys.exit(1)
        return False
    return True


def init_logger (app, conf):
    # 0. Parse conf
    # 0.1 path
    log_raw_path = conf['logger']['path']
    log_path = os.path.join(base_dir, log_raw_path) if not os.path.isabs(log_raw_path) else log_raw_path

    # 0.2 log_level
    #   log_level は  DEBUG, INFO, WARNING, ERROR, CRITICAL, から選択のこと。
    level_str = conf['logger']['log_level'].upper()
    if not is_log_level_exists_in_logging_p__otherwise__errror_and_exit (level_str):
        sys.exit(1)

    log_level = logging._nameToLevel[level_str]
    
    # 1. ログファイルを生成
    if log_path:
        make_path_dir_if_not_exists(log_path)
    file_handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=5)

    # 2. フォーマットを決定
    formatter_pattern = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    file_handler.setFormatter(logging.Formatter(formatter_pattern))

    # Log Level の設定
    file_handler.setLevel(log_level)
    app.logger.setLevel(log_level)

    # Flask 標準のロガーに設定を反映
    app.logger.addHandler(file_handler)

    # return
    return app.logger


def register_gate_to_app(app, name, GateClass, config, db_session, logger, template_dir):
    """
    Instantiate a Gate class and register its Blueprint to the Flask application.
    This factory function encapsulates the entire setup process for each Gate.
    """

    # 1. Initialize Blueprint with the specified name and template directory.
    bp = Blueprint(name, __name__, template_folder=template_dir)

    # 2. Instantiate the Gate class by invoking its constructor with config and session.
    ctrl = GateClass(config=config, db_session=db_session, logger=logger)

    # 3. Register Blueprint to ctrl
    ctrl.register(bp)

    # 4. Register the configured Blueprint to the main Flask application.
    app.register_blueprint(bp)

    # Return
    return app, ctrl


def create_app(conf):

    # Init APP
    app = Flask(__name__, static_folder=assets_folder)
    app.secret_key = conf['app_secret_key']

    # Init DataBase
    init_database(app, conf)

    # Init logger
    logger = init_logger(app, conf)

    # Config template dir
    app.template_folder = template_dir


    # Register gates to app

    # 1. Gate definitions as [('name', Constructor)]
    gate_definitions = [('portal',   PortalGate),
                        ('facemans', FacemanGate),
                        ('tolopica', TolopicaGate),
                        ('ranference', RanferenceGate)]

    # 2. Functional Reduction without 'def'
    # We use a lambda to process each registration and return the updated app.
    app = reduce(lambda acc_app, gate_def:
                 register_gate_to_app(acc_app, gate_def[0], gate_def[1],
                                      conf, db.session, logger, template_dir)[0],
                 gate_definitions,
                 app)

    # Return
    return app


# main
if __name__ == '__main__':
    # Parse conf
    conf = read_config_yaml(config_file_path, config_YAML_required_schemas)

    # create app
    app = create_app(conf)

    with app.app_context():
        db.create_all()

    port = conf['server']['port']
    debug = conf['server']['debug']

    app.run(host='0.0.0.0', port=5000, debug=True)
