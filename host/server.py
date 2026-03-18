# -*- coding: utf-8 -*-
from functools import reduce
#
import os
import sys
from flask import Flask, Blueprint
# application
from read_config import read_config_yaml
from models import db
from routes.portal_gate import PortalGate
from routes.post_gate import PostGate
from routes.faceman_gate import FacemanGate
from routes.tolopica_gate import TolopicaGate



# Configs
config_YAML_required_schemas = {
    'database': {'path': str, 'track_modifications': bool},
    'server': {'port': int, 'debug': bool},
    'app_secret_key': str
}

## path configs
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
config_file_path = os.path.join(base_dir, './config.yaml')
assets_folder = os.path.join(base_dir, './host/static/')
template_dir = os.path.join(base_dir, './host/templates/')


# Init System
def init_database (app, conf):

    # Parse conf
    db_modify = conf['database']['track_modifications']
    db_raw_path = conf['database']['path']
    db_path = os.path.join(base_dir, db_raw_path) if not os.path.isabs(db_raw_path) else db_raw_path


    # Configure DB
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_modify

    # Initialize DB
    db.init_app(app)

    # Return
    return app


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


def create_app(conf):

    # Init APP
    app = Flask(__name__, static_folder=assets_folder)
    app.secret_key = conf['app_secret_key']

    # Init DataBase
    init_database(app, conf)

    # Config template dir
    app.template_folder = template_dir

    # Register gates to app

    # 1. Gate definitions as [('name', Constructor)]
    gate_definitions = [('portal',   PortalGate),
                        ('posts',    PostGate),
                        ('facemans', FacemanGate),
                        ('tolopica', TolopicaGate),]

    # 2. Functional Reduction without 'def'
    # We use a lambda to process each registration and return the updated app.
    app = reduce(lambda acc_app, gate_def:
                 register_gate_to_app(acc_app, gate_def[0], gate_def[1], conf, db.session, template_dir)[0],
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
    app.run(host='0.0.0.0', port=port, debug=debug)
