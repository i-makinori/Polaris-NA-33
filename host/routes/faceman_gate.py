# -*- coding: utf-8 -*-
from flask import flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import Known_Person


# velificate form texts

import re

def is_ok_password_text(password_1, password_2):
    # 0. Password equally
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


def is_ok_email_text(email_text_p):
    # 0. email text exists.
    if not email_text_p:
        return False, "メールアドレスを入力してください。"
    # 1. 基本構造のチェック (RFC5322に準拠した実用的な正規表現)
    # ユーザー名部分は英数字と一部の記号、ドメイン部分は英数字とハイフン、最後に2文字以上のTLD
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email_text_p):
        return False, "メールアドレスの形式が正しくありません。"
    # 2. 連続するドットの禁止 (例: a..b@example.com)
    if '..' in email_text_p:
        return False, "ドットが連続しているアドレスは使用できません。"
    # 3. 全体的な長さ制限 (RFC準拠: 合計254文字まで)
    if len(email_text_p) > 254:
        return False, "メールアドレスが長すぎます。"
    # *. Success
    return True, ""


def is_ok_faceman_id_text(faceman_id_text_p):
    # 0. form value exists.
    if not faceman_id_text_p:
        return False, "ユーザIDを入力してください。"
    # 1. regex check. Allowed signs is '_' and '-'.
    id_regex = r'^[a-zA-Z0-9_-]+$'  # ハイフン記号のregexの登録でエスケープを用いる。
    if not re.match(id_regex, faceman_id_text_p):
        return False, "IDには英数字、アンダースコア(_)、ハイフン(-)のみ使用可能です。"
    # 2. 文字数のチェック
    if not (6 <= len(faceman_id_text_p) <= 20):
        return False, "IDは6文字以上20文字以内で設定してください。"
    # 3. 予約語のチェック (これを忘れると /user/admin のようなURLを乗っ取られる可能性がある)
    reserved_words = {'admin', 'root', 'system', 'config', 'guest', 'signup', 'signin', 'login'}
    if faceman_id_text_p.lower() in reserved_words:
        # return False, "そのIDはシステム予約語のため使用できません。"
        return False, "そのIDは登録されています。"
    # *. Success
    return True, ""


# session names
# pass

# Routes for FacemanGate

class FacemanGate:
    def __init__(self, config,db_session):
        self.config = config
        self.db = db_session

    def signup_get(self):
        return render_template('signup.html')

    def signup_post(self):
        # 1.  handle posted datas
        d = request.form
        name, text_id, email = d.get('name'), d.get('text_id'), d.get('email')
        p1, p2 = d.get('password_1'), d.get('password_2')

        errors = []
        ctx = {'form_name': name, 'form_text_id': text_id, 'form_email': email}

        # 2. Validations
        # 2.1 detect that all items are filled
        if not (name and text_id and email and p1 and p2):
            errors += ['全項目を入力して下さい。']

        # 2.2 password check
        password_is_valid, password_error_message = is_ok_password_text(p1, p2)
        if not password_is_valid:
            errors += [password_error_message]

        # 2.3 email check
        email_text_is_valid, email_text_error_message = is_ok_email_text(email)
        if not email_text_is_valid:
            errors += [email_text_error_message]


        ## Check DB collision (email)
        if Known_Person.query.filter_by(email=email).first():
            errors += ["このメールアドレスは既に登録されています。"]

        # 2.4 text_id check
        text_id_text_is_valid, text_id_text_error_message = is_ok_faceman_id_text(text_id)
        if not text_id_text_is_valid:
            errors += [text_id_text_error_message]

        ## Check DB collision (text_id)
        if Known_Person.query.filter_by(text_id=text_id).first():
            errors += ["このユーザIDは既に使用されています。別のIDをお試しください。"]

        # 2. R if some errors, return with error message
        if errors != [] :
            return render_template('signup.html', error=errors, **ctx)

        # 3 new_user の鋳型の作成
        new_user = Known_Person(name=name,
                                email=email,
                                text_id=text_id,
                                password=generate_password_hash(p1))
        # 4 DB write (maybe exceptions)
        try:
            self.db.add(new_user)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)
            error_message = "server_error"
            return render_template('tolopica_add.html', error=error_message, **ctx) # exception page

        # 5. success
        # 5.1 signin
        self.state_signin(text_id, p1)

        # 5.2 context(ctx)
        ctx |= { # append
            'tml_message' : f"{name}さんは、id {text_id} かつ、 email {email} にてユーザ登録されました。",
            'tml_title' : "ユーザ登録完了"
        }

        # 5.3 render
        return render_template('message.html', **ctx)

    def signin_get(self):
        return render_template('signin.html')

    def signin_post(self):
        d = request.form
        text_id = d.get('text_id')
        password = d.get('password')
        # 認証
        detect_signin = self.state_signin(text_id, password)
        # 画面表示
        if detect_signin==True: # 認証成功
            return redirect(url_for('portal.index'))
        else: # 認証失敗
            error_text = "ユーザIDまたはパスワードが正しくありません。"
            return render_template('signin.html', error_text=error_text)

    def signout_get(self):
        self.state_signout()
        return redirect(url_for('portal.index'))

    def state_signin(self, user_id, password_hash_text):
        # 1. ユーザーをDBから探す (ID または Email でログイン可能にするのが一般的)
        user = Known_Person.query.filter_by(text_id=user_id).first() # ID で探す。

        # 2. ユーザーが存在し、かつパスワードが一致するか検証
        if user and check_password_hash(user.password, password_hash_text): # 認証成功！
            self.state_signout() # セキュリティのため一度クリア
            # セッションに刻む
            session['user_id'] = user.id
            session['user_name'] = user.name
            return True
        else: # 認証失敗
            return False

    def state_signout(self):
        session.clear() # is too strong
        #
        # session.pop('user_id', None)
        # session.pop('user_name', None)

        return None

    def register(self, bp):
        # signup
        bp.add_url_rule('/signup', view_func=self.signup_get,  methods=['GET'],  endpoint='signup_get')
        bp.add_url_rule('/signup', view_func=self.signup_post, methods=['POST'], endpoint='signup_post')
        # signin
        bp.add_url_rule('/signin', view_func=self.signin_get,  methods=['GET'],  endpoint='signin_get')
        bp.add_url_rule('/signin', view_func=self.signin_post, methods=['POST'], endpoint='signin_post')
        # signout
        bp.add_url_rule('/signout', view_func=self.signout_get, methods=['GET'],  endpoint='signout_get')
