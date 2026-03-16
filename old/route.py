# -*- coding: utf-8 -*-


from flask import render_template, request, redirect, url_for

class PostGate:
    def __init__(self, db_session):
        self.db = db_session  # DBセッションなどを注入可能

    def index(self):
        return "スレッド一覧画面"

    def detail(self, post_id):
        return f"スレッド詳細: {post_id}"

    def create(self):
        if request.method == 'POST':
            # 書き込み処理
            return redirect(url_for('posts.index'))
        return "新規作成画面"

    # ここでルートを一括登録する
    def register(self, bp):
        bp.add_url_rule('/', view_func=self.index, endpoint='index')
        bp.add_url_rule('/<int:post_id>', view_func=self.detail, endpoint='detail')
        bp.add_url_rule('/create', view_func=self.create, methods=['GET', 'POST'], endpoint='create')



