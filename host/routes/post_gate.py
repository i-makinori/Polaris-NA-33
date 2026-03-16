# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for
from models import Post  # モデルをインポート

class PostGate:
    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def index(self):
        # 以前の index ロジック
        posts = Post.query.order_by(Post.created_at.desc()).all()
        # リスト内包表記で、各 Post を辞書化して文字列にする
        serialized_posts = [str(post.__dict__) for post in posts]
        
        return f'posts: {serialized_posts}'

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


# class MainGate:
#     def __init__(self, config, db_session, models):
#         self.config = config
#         self.db = db_session
#         self.Post = models.Post # モデルも外部から受け取る（徹底した脱マジック）

#     def index(self):
#         # 以前の Post.query.all() ではなく、明示的に session から select する
#         stmt = select(self.Post).order_by(self.Post.created_at.desc())
#         posts = self.db.execute(stmt).scalars().all()
#         return render_template('index.html', posts=posts, config=self.config)

#     def index_redirect(self):
#         return redirect(url_for('main.index'))

#     def tolopica_add(self):
#         if request.method == 'POST':
#             # トピック追加ロジック...
#             pass
#         return render_template('tolopica_add.html')

#     def tolopica_view(self, tolopica_name):
#         # パラメータ ?id=... の取得は request.args から
#         target_id = request.args.get('id')
#         # 表示ロジック...
#         return render_template('tolopica.html', name=tolopica_name, target_id=target_id)

#     def ranference_redirect(self, ranference_id):
#         # id から tolopica_name を逆引きしてリダイレクト
#         # 本来はDBから引くが、ここでは概念のみ
#         tolopica_name = "example_topic" 
#         return redirect(url_for('main.tolopica_view', tolopica_name=tolopica_name, id=ranference_id))

#     def register(self, bp):
#         bp.add_url_rule('/', view_func=self.index, endpoint='index')
#         bp.add_url_rule('/index.html', view_func=self.index_redirect)
#         bp.add_url_rule('/tolopica_add', view_func=self.tolopica_add, methods=['GET', 'POST'])
#         bp.add_url_rule('/tolopica/<tolopica_name>', view_func=self.tolopica_view)
#         bp.add_url_rule('/ranference/<int:ranference_id>', view_func=self.ranference_redirect)


# class ParambasisGate:
#     def __init__(self, config, db_session):
#         self.config = config
#         self.db = db_session

#     def _check_admin(self):
#         """魔法（before_request）を使わず、各関数で明示的に呼ぶ『脱ブラックボックス』スタイル"""
#         if not session.get('is_admin'):
#             abort(403) # Forbidden

#     def edit_index(self):
#         self._check_admin()
#         return render_template('admin/edit_index.html')

#     def edit_tolopica(self):
#         self._check_admin()
#         return "ToLopica Edit Page"

#     def del_ranference(self):
#         self._check_admin()
#         return "RanFerence Delete Action"

#     def edit_parapara(self):
#         self._check_admin()
#         return "Admin Settings"

#     def register(self, bp):
#         # prefix は Blueprint 側で '/parambasis_pp' と指定される想定
#         bp.add_url_rule('/edit_index', view_func=self.edit_index)
#         bp.add_url_rule('/edit_tolopica', view_func=self.edit_tolopica)
#         bp.add_url_rule('/del_ranference', view_func=self.del_ranference, methods=['POST'])
#         bp.add_url_rule('/edit_parapara', view_func=self.edit_parapara)
