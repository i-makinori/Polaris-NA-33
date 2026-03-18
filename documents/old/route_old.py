# -*- coding: utf-8 -*-
# $ python3 ./route_old.py
#
# host/route.py
import os
import yaml
from pathlib import Path
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Flask instance
app = Flask(__name__)

# configs for file
base_dir = Path(__file__).resolve().parent.parent

config_path = os.path.join(base_dir, 'config.yaml')
templates_path = os.path.join(base_dir, 'host/templates/')

## Open config file
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

## parse config Parameters.
db_raw_path = config['database']['path']
if not os.path.isabs(db_raw_path): # case by Absolute path or Relative Path
    db_path = os.path.join(base_dir, db_raw_path)
else:
    db_path = db_raw_path

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['database'].get('track_modifications', False)

db = SQLAlchemy(app)

## read port and debug
port = config['server'].get('port', 5000)  # 値がない場合のデフォルト値は5000
debug = config['server'].get('debug', False) # 値がない場合のデフォルト値はFalse


## Specify the location of the template.

app.template_folder = templates_path


# DataBase and Data Classes

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Routes

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post', methods=['POST'])
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    new_post = Post(title=title, content=content)
    db.session.add(new_post)
    db.session.commit()
    return redirect('/')


# main

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port, debug=debug)
