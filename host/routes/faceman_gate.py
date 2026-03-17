
from flask import flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from models import Known_Person

import re

def is_ok_password(password_1, password_2):
    if password_1 != password_2:
        return False, "パスワードが一致しません。"
    
    # 1. ASCIIコードのみかチェック (0x00 - 0x7F)
    if not all(ord(c) < 128 for c in password_1):
        return False, "パスワードには半角英数字のみ使用できます。"

    # 2. 8文字以上かチェック
    if len(password_1) < 8:
        return False, "パスワードは8文字以上必要です。"

    # 3. 数字が含まれているかチェック
    if not re.search(r'\d', password_1):
        return False, "パスワードには少なくとも1つの数字を含めてください。"

    # 4. アルファベットが含まれているかチェック
    if not re.search(r'[a-zA-Z]', password_1):
        return False, "パスワードには少なくとも1つの英字を含めてください。"

    return True, ""

session_name_signup_error = 'signup_error'

def raise_client_signup_error(message):
    session[session_name_signup_error] = message
    return session

class FacemanGate:
    def __init__(self, db_session):
        self.db = db_session

    def signup_get(self):
        error_text = session.pop(session_name_signup_error, None)
        return render_template('signup.html', error_text=error_text)

    def signup_post(self):
        # 1.  handle posted datas
        d = request.form
        name, email = d.get('name'), d.get('email')
        p1, p2 = d.get('password_1'), d.get('password_2')
        # todo : read text ID

        # 2. Validations
        # 2.1 all items
        if not (name and email and p1 and p2):
            raise_client_signup_error('全項目を入力して下さい。')
            return redirect(url_for('facemans.signup_get'))

        # 2.2 password check
        password_is_valid, password_error_message = is_ok_password(p1, p2)
        if not password_is_valid:
            raise_client_signup_error(password_error_message)
            return redirect(url_for('facemans.signup_get'))

        # 2.3 DB write (maybe exceptions)
        try:
            new_user = Known_Person(
                name=name,
                email=email,
                # todo : read text ID
                password=generate_password_hash(p1)
            )
            self.db.add(new_user)
            self.db.commit()

        except IntegrityError:
            self.db.rollback()
            raise_client_signup_error("そのtext_id あるいは メールアドレスは既に使用されています。")
            return redirect(url_for('facemans.signup_get'))

        # 3. success
        ctx = {
            'tml_message' : f"{name}さんは、email {email} にてユーザ登録されました。",
            'tml_title' : "ユーザ登録完了"
        }
        return render_template('message.html', **ctx)

    def register(self, bp):
        bp.add_url_rule('/signup', view_func=self.signup_get, methods=['GET'], endpoint='signup_get')
        bp.add_url_rule('/signup', view_func=self.signup_post, methods=['POST'], endpoint='signup_post')
