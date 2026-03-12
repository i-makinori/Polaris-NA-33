# -*- coding: utf-8 -*-
import os
import yaml
from pathlib import Path
from datetime import datetime
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

# --- 1. 専門マネージャークラス (部品) ---

class ThreadManager:
    """スレッドとレスポンスの読み書きに特化したクラス"""
    def __init__(self, db, models):
        self.db = db
        self.Post = models['Post']
        self.Reply = models['Reply']

    def create_thread(self, title, content):
        new_post = self.Post(title=title, content=content)
        self.db.session.add(new_post)
        self.db.session.commit()
        return new_post

    def post_reply(self, thread_id, content):
        # ここで将来的に「数式バリデーター」などを挟むことが可能
        reply = self.Reply(thread_id=thread_id, content=content)
        self.db.session.add(reply)
        self.db.session.commit()

class AdminManager:
    """管理者専用の操作（削除、議題追加など）を担うクラス"""
    def __init__(self, db, models):
        self.db = db
        self.Post = models['Post']

    def delete_post(self, post_id):
        post = self.Post.query.get(post_id)
        if post:
            self.db.session.delete(post)
            self.db.session.commit()

# --- 2. 統合司令塔クラス (本体) ---

class BBSCore:
    """
    Flask, DB, 各種マネージャーをすべて内包し、
    システム全体をまとめ上げるメインクラス
    """
    def __init__(self, config_path=None):
        # A. 設定の初期化
        self.base_dir = Path(__file__).resolve().parent.parent
        self.config_path = config_path or (self.base_dir / 'config.yaml')
        self._load_config()

        # B. Flask & DB の初期化
        self.app = Flask(__name__)
        self.app.template_folder = str(self.base_dir / 'host' / 'templates')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.db = SQLAlchemy(self.app)

        # C. モデルの定義 (dbインスタンスが必要なためここで定義)
        self._define_models()

        # D. 各専門マネージャーの集約 (コンポジション)
        models = {'Post': self.Post, 'Reply': self.Reply}
        self.thread_manager = ThreadManager(self.db, models)
        self.admin_manager = AdminManager(self.db, models)

        # E. ルーティングの登録
        self._register_routes()

    def _load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        db_raw = Path(data['database']['path'])
        self.db_uri = f"sqlite:///{self.base_dir / db_raw}"
        self.port = data['server'].get('port', 5000)
        self.debug = data['server'].get('debug', False)

    def _define_models(self):
        class Post(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            title = self.db.Column(self.db.String(100), nullable=False)
            content = self.db.Column(self.db.Text, nullable=False)
            created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)

        class Reply(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            thread_id = self.db.Column(self.db.Integer, nullable=False)
            content = self.db.Column(self.db.Text, nullable=False)
            created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)

        self.Post = Post
        self.Reply = Reply

    def _register_routes(self):
        """エンドポイントをFlaskインスタンスに紐付ける"""
        
        @self.app.route('/')
        def index():
            posts = self.Post.query.order_by(self.Post.created_at.desc()).all()
            # 簡易表示用。本来は render_template('index.html', posts=posts)
            #return f"Thread count: {len(posts)}"
            return render_template('index.html', posts=posts)

        @self.app.route('/post', methods=['POST'])
        def create_thread():
            title = request.form.get('title')
            content = request.form.get('content')
            self.thread_manager.create_thread(title, content)
            return redirect('/')

    def run(self):
        """データベースを作成し、サーバーを起動する"""
        with self.app.app_context():
            self.db.create_all()
        self.app.run(host='0.0.0.0', port=self.port, debug=self.debug)


# --- モデル定義の変更点 ---
def _define_models(self):
    class Board(self.db.Model):
        id = self.db.Column(self.db.Integer, primary_key=True)
        slug = self.db.Column(self.db.String(20), unique=True, nullable=False) # url用
        name = self.db.Column(self.db.String(50), nullable=False)

    class Thread(self.db.Model):
        id = self.db.Column(self.db.Integer, primary_key=True)
        board_id = self.db.Column(self.db.Integer, self.db.ForeignKey('board.id'), nullable=False)
        title = self.db.Column(self.db.String(100), nullable=False)
        created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)

    class Post(self.db.Model):
        id = self.db.Column(self.db.Integer, primary_key=True)
        thread_id = self.db.Column(self.db.Integer, self.db.ForeignKey('thread.id'), nullable=False)
        content = self.db.Column(self.db.Text, nullable=False)
        created_at = self.db.Column(self.db.DateTime, default=datetime.utcnow)

    self.Board, self.Thread, self.Post = Board, Thread, Post


# --- 3. 実行セクション ---

if __name__ == "__main__":
    # システムのインスタンスを一つ作るだけで、すべてが準備される
    bbs_system = BBSCore()
    bbs_system.run()
