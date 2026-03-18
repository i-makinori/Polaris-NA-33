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
    """
    Main interface for configuration validation.
    The actual recursive logic is delegated to the auxiliary function.
    """
    required_schema = {
        'database': {'path': str, 'track_modifications': bool},
        'server': {'port': int, 'debug': bool},
        'app_secret_key': str
    }
    
    # Delegate to the auxiliary function
    return _validate_config_aux(conf, required_schema, path="")

def _validate_config_aux(conf, schema, path):
    """
    Auxiliary recursive function to traverse and validate the config tree.
    """
    for key, expected in schema.items():
        current_path = f"{path}.{key}" if path else key
        
        # 1. Existence check
        if key not in conf:
            raise ValueError(f"Configuration Error: Missing required key '{current_path}'.")

        actual_val = conf[key]

        # 2. Recursive step (Vertical traversal)
        if isinstance(expected, dict):
            if not isinstance(actual_val, dict):
                raise TypeError(f"Configuration Error: '{current_path}' must be a dictionary.")
            _validate_config_aux(actual_val, expected, current_path)
        
        # 3. Base case (Leaf node validation)
        else:
            if not isinstance(actual_val, expected):
                raise TypeError(
                    f"Configuration Error: '{current_path}' must be of type {expected.__name__}. "
                    f"Got {type(actual_val).__name__} instead."
                )
    return True

def read_config(config_path):
    # Open config file and Valuate to conf
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
    except Exception as e:
        print(f"Config Error: {e}")
        sys.exit(1)

    # Validate conf
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
