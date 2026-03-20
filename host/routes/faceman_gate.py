# -*- coding: utf-8 -*-
from flask import flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import Known_Person


# velificate form texts

import re

def validate_val_by_rules(default_test, default_mess, otherwise_rules):
    """
    default_test: True の場合、即座に [default_mess] を返す
    otherwise_rules: (エラー条件, メッセージ) のリスト。条件が True のものを抽出する
    """
    errors = []

    if default_test:
        errors = [default_mess]
    else:
        # 地雷（True）を踏んでいるメッセージだけをリストにして返す
        errors = [msg for condition, msg in otherwise_rules if condition]

    return errors



RE_DIGIT = re.compile(r'\d')
RE_ALPHA = re.compile(r'[a-zA-Z]')
RE_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
RE_FACEMAN_ID_FORMAT = re.compile(r'^[a-zA-Z0-9_-]+$')

RESERVED_WORDS = {'admin', 'root', 'system', 'config', 'guest', 'signup', 'signin', 'login'}


def is_bad_faceman_name_text_p(name):
    return validate_val_by_rules(
        name == "", "名前を入力してください。",
        [(not (1 <= len(name) <= 100), "名前は1文字以上100文字以内で入力してください。"),
         ('\n' in name or '\r' in name, "名前には改行を使用できません。"),
         (name.strip() == "", "名前は空白以外の文字を含めてください。")
        ])

def is_bad_email_text_p(email):
    return validate_val_by_rules(
        email == "", "メールアドレスを入力してください。",
        [(RE_EMAIL.match(email) is None, "メールアドレスの形式が正しくありません。"),
         ('..' in email, "ドットが連続しているアドレスは使用できません。"), # not を外しました
         (len(email) > 254, "メールアドレスが長すぎます。")
        ])

def is_bad_faceman_id_text_p(id_text):
    return validate_val_by_rules(
        id_text == "", "ユーザIDを入力してください。",
        [(RE_FACEMAN_ID_FORMAT.match(id_text) is None, "IDには英数字、アンダースコア(_)、ハイフン(-)のみ使用可能です。"),
         (not (6 <= len(id_text) <= 100), "IDは6文字以上100文字以内で設定してください。"),
         (id_text.lower() in RESERVED_WORDS, "そのIDは登録されています。")
        ])

def is_bad_password_text_p(p1, p2):
    return validate_val_by_rules(
        (p1 == "" or p2 == ""), "パスワードを入力してください。",
        [(p1 != p2, "パスワードが一致しません。"),
         (not (8 <= len(p1) <= 120), "パスワードは8文字以上120文字以下としてください。"),
         (not p1.isascii(), "パスワードには半角英数字のみ使用できます。"),
         (RE_DIGIT.search(p1) is None, "パスワードには少なくとも1つの数字を含めてください。"),
         (RE_ALPHA.search(p1) is None, "パスワードには少なくとも1つの英字を含めてください。")
        ])




# session names
# pass

# Routes for FacemanGate

class FacemanGate:
    def __init__(self, config,db_session):
        self.config = config
        self.db = db_session

    @staticmethod
    def _signup_post_errors(name, text_id, email, p1, p2):
        """
        全てのバリデーションを実行し、エラーメッセージのリストを返す。
        DB照合などの「外部への副作用」を伴うチェックもここに集約する。
        """
        errors = []

        # 1. 必須項目チェック（ガード節）
        if not (name and text_id and email and p1 and p2):
            return ["全項目を入力して下さい。"]

        # 2. 各フィールドの形式チェック（地雷リストの結合）
        errors += is_bad_faceman_name_text_p(name)
        errors += is_bad_faceman_id_text_p(text_id)
        errors += is_bad_email_text_p(email)
        errors += is_bad_password_text_p(p1, p2)

        # 3. DB重複チェック
        if Known_Person.query.filter_by(text_id=text_id).first():
            errors.append("このユーザIDは既に使用されています。別のIDをお試しください。")
        if Known_Person.query.filter_by(email=email).first():
            errors.append("このメールアドレスは既に登録されています。")

        # R. return
        return errors


    def signup_get(self):
        return render_template('signup.html')


    def signup_post(self):
        # 1. variables setting. (and also getting).
        # 1.1 handle posted datas
        form_dict = request.form
        keys = ('name', 'text_id', 'email', 'password_1', 'password_2')
        name, text_id, email, p1, p2 = map(form_dict.get, keys)
        # 1.2. make context (ctx) .
        ctx = {'form_name': name, 'form_text_id': text_id, 'form_email': email}

        # 2. Validations
        errors = self._signup_post_errors(name, text_id, email, p1, p2)
        # 2.R. if some errors, return with error message.
        if errors != [] :
            return render_template('signup.html', error=errors, **ctx)
        # if p1 != p2 :
        #     return render_template('signup.html', error=["パスワードが一致しません。"], **ctx)

        # 3 new_user の鋳型の作成
        hash_pass = generate_password_hash(p1) # assume p1 == p2
        new_user = Known_Person(name=name, email=email, text_id=text_id, password=hash_pass)
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
