# -*- coding: utf-8 -*-
# $ python3 ./route.py
#
# host/route.py
import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# configs

## Specify the location of the template.
base_dir = os.path.dirname(os.path.abspath(__file__)) # <currentdirectory of this python file>
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates')) 

## データベースファイルも host フォルダ内に作成
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, 'bbs.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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
    app.run(debug=True)


