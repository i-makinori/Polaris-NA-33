# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for
from models import Post  # モデルをインポート

class PostController:
    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def index(self):
        # 以前の index ロジック
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template('index.html', posts=posts, config=self.config)

    def create(self):
        # 以前の create_post ロジック
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            new_post = Post(title=title, content=content)
            self.db.add(new_post)
            self.db.commit()
            return redirect(url_for('posts.index'))
        
        return render_template('create.html') # 必要に応じて追加

    def register(self, bp):
        bp.add_url_rule('/', view_func=self.index, endpoint='index')
        bp.add_url_rule('/post', view_func=self.create, methods=['POST'], endpoint='create')


