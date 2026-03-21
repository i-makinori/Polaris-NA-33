# -*- coding: utf-8 -*-
from flask import redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from utils import logger_text, get_values_from_dict, GateABC
from models import Known_Person, Tolopica, Ranference


# todo:
# セキュリティチェック：ログイン済みかつ is_admin が True
# return user is not None and getattr(user, 'is_admin', False)
# is_admin 列を、Known_Peron table へと追加。

# todo:
# routing の一覧へと追加。


# 2. アクセス制限付きの基底 View クラス

class AdminGate(GateABC):
    def register(self, bp):
        """
        Admin は Blueprint ではなく app に直接紐付くため、
        bp.record を使って遅延実行（app が確定したタイミングで登録）させます。
        """
        # setup_admin 自体は以前作成したものを流用
        def deferred_admin_setup(state):
            setup_admin(state.app, self.db)
            
        bp.record(deferred_admin_setup)

    # index などは setup_admin 側で Flask-Admin が生成するので
    # ここに個別の view メソッドを書く必要はありません。




class MyModelView(ModelView):
    def is_accessible(self):
        """
        GateABC と同様に request オブジェクトのキャッシュを参照する。
        """
        # request._cached_user_till_request がセットされていることを期待
        # もしセットされていない場合に備え、Gate の current_user と同様のロジックを保険で入れる
        user = getattr(request, '_cached_user_till_request', None)
        
        # セキュリティチェック：ログイン済みかつ is_admin が True
        return user is not None and getattr(user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        """権限がない場合の挙動"""
        flash("管理者以外は立ち入り禁止です。宇宙の彼方へとお帰りください。")
        return redirect(url_for('facemans.signin_get'))


# 各 Table 毎の表示方式

class UserModelView(MyModelView):
    # 一覧や編集フォームからパスワードを除外する
    column_exclude_list = ['password', ]
    form_excluded_columns = ['password', ]

class TolopicaModelView(MyModelView):
    # 一覧に表示するカラム
    column_list = ['id', 'text_id', 'title', 'created_at']
    # 並び順を ID 降順に
    column_default_sort = ('id', True)
    # 検索対象にするカラム（板のタイトルやIDで検索可能に）
    column_searchable_list = ['title', 'text_id']


class RanferenceModelView(MyModelView):
    # 一覧に表示するカラムを絞る
    column_list = ['id', 'author', 'content', 'coding_type', 'tolopica_id']
    # 内容を 50 文字で切り詰めて表示
    column_formatters = {
        'content': lambda v, c, m, p: (m.content[:50] + '...') if m.content and len(m.content) > 50 else m.content
    }



# admin_page のsetup

def setup_admin(app, db):
    """
    アプリケーションに管理画面をセットアップする。
    """
    # 1. Admin インスタンスの作成
    # index_view を指定することで、管理画面のトップ自体のアクセス制限も可能になります
    # admin = Admin(app, name='Polaris-NA-33 Admin', template_mode='bootstrap4', url='/admin')
    admin = Admin(app, name='Polaris-NA-33 Admin', url='/admin')

    # 2. 各モデルを管理画面に登録
    ## 表示制限有り
    ## ... MyModelView を継承したクラスを使うことで、すべてのページに表示制限が適用される。
    admin.add_view(UserModelView(Known_Person, db, name="ユーザー管理", endpoint="admin_user"))
    admin.add_view(TolopicaModelView(Tolopica, db, name="板管理", endpoint="admin_tolopica"))
    admin.add_view(RanferenceModelView(Ranference, db, name="投稿管理", endpoint="admin_ranference"))
    
    ## 表示制限無し
    # admin.add_view(MyModelView(Known_Person, db, name="ユーザー管理", endpoint="admin_user"))
    # admin.add_view(MyModelView(Tolopica, db, name="板管理", endpoint="admin_tolopica"))
    # admin.add_view(MyModelView(Ranference, db, name="投稿管理", endpoint="admin_ranference"))

    # R. return
    return admin

