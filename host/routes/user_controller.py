
from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from models import Known_Person

class UserController:
    def __init__(self, db_session):
        self.db = db_session

    def signup_get(self):
        return render_template('signup.html')

    def signup_post(self):
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password') # todo: password の重複チェック。

        # ハッシュ化して保存
        new_user = Known_Person(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        try:
            self.db.add(new_user)
            self.db.commit()
        except IntegrityError:
            # 重複発生時のロールバック
            self.db.rollback()
            return "そのメールアドレスは既に登録されています。<br /><a href='/'>index<a>に戻ります。"

        finally:
            return "登録されました。 <br /><a href='/'>index<a>に戻ります。"

    def register(self, bp):
        bp.add_url_rule('/signup', view_func=self.signup_get, methods=['GET'], endpoint='signup_get')
        bp.add_url_rule('/signup', view_func=self.signup_post, methods=['POST'], endpoint='signup_post')
