# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for

class PostController:
    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def index(self):
        # YAMLの構造に合わせてアクセス (例: conf_data['board']['title'])
        title = self.config.get('board', {}).get('title', 'BBS')
        return f"<h1>{title}</h1>スレッド一覧画面"

    def detail(self, post_id):
        return f"スレッド詳細: {post_id}"

    def create(self):
        if request.method == 'POST':
            # ここで self.db を使って保存処理を行う
            return redirect(url_for('posts.index'))
        return "新規作成画面"

    def register(self, bp):
        # endpoint を 'posts.index' 形式にするため、あえてクラス外から呼ばれる想定
        bp.add_url_rule('/', view_func=self.index, endpoint='index')
        bp.add_url_rule('/<int:post_id>', view_func=self.detail, endpoint='detail')
        bp.add_url_rule('/create', view_func=self.create, methods=['GET', 'POST'], endpoint='create')
