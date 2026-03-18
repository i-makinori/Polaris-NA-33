
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
    # 1. regex check. Allowed signs is _ - ^ + /
    id_regex = r'^[a-zA-Z0-9_^+/\-]+$'  # ハイフン記号のregexの登録でエスケープを用いる。
    if not re.match(id_regex, faceman_id_text_p):
        return False, "IDに使用できない文字が含まれています。(_-^+/ が使用可能です)"
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
session_name_signup_error = 'signup_error'
session_name_signin_error = 'signin_error'

# Routes for FacemanGate

def raise_FacemanGate_client_signup_error(message):
    session[session_name_signup_error] = message
    return redirect(url_for('facemans.signup_get'))

class FacemanGate:
    def __init__(self, config,db_session):
        self.config = config
        self.db = db_session

    def signup_get(self):
        error_text = session.pop(session_name_signup_error, None)
        return render_template('signup.html', error_text=error_text)

    def signup_post(self):
        # 1.  handle posted datas
        d = request.form
        name, text_id, email = d.get('name'), d.get('text_id'), d.get('email')
        p1, p2 = d.get('password_1'), d.get('password_2')
        # todo : read text ID

        # 2. Validations
        # 2.1 detect that all items are filled
        if not (name and text_id and email and p1 and p2):
            return raise_FacemanGate_client_signup_error('全項目を入力して下さい。')

        # 2.2 password check
        password_is_valid, password_error_message = is_ok_password_text(p1, p2)
        if not password_is_valid:
            return raise_FacemanGate_client_signup_error(password_error_message)

        # 2.3 email check
        email_text_is_valid, email_text_error_message = is_ok_email_text(email)
        if not email_text_is_valid:
            return raise_FacemanGate_client_signup_error(email_text_error_message)


        ## Check DB collision (email)
        if Known_Person.query.filter_by(email=email).first():
            return raise_FacemanGate_client_signup_error("このメールアドレスは既に登録されています。")

        # 2.4 text_id check
        text_id_text_is_valid, text_id_text_error_message = is_ok_faceman_id_text(text_id)
        if not text_id_text_is_valid:
            return raise_FacemanGate_client_signup_error(text_id_text_error_message)

        ## Check DB collision (text_id)
        if Known_Person.query.filter_by(text_id=text_id).first():
            return raise_FacemanGate_client_signup_error("このユーザIDは既に使用されています。別のIDをお試しください。")

        # 2.5 DB write (maybe exceptions)
        try:
            # print(f"DEBUG: DB 登録開始 - {name}, {text_id}") # debug
            new_user = Known_Person(name=name,
                                    email=email,
                                    text_id=text_id,
                                    password=generate_password_hash(p1))
            self.db.add(new_user)
            self.db.commit()
            # print("DEBUG: DB 登録成功！") # debug

        except IntegrityError:
            self.db.rollback()
            return raise_FacemanGate_client_signup_error("その text_id あるいは email は、既に使用されています。")

        # 3. success
        # by AI        # 3.1 auto signin
        #         # 登録したてのユーザーIDをセッションに刻む（自動ログイン）
        #         session['user_id'] = new_user.id
        # by AI        session['user_name'] = new_user.name
        # 3.2 context(ctx)
        ctx = {
            'tml_message' : f"{name}さんは、email {email} にてユーザ登録されました。",
            'tml_title' : "ユーザ登録完了"
        }
        # 3.3 render
        return render_template('message.html', **ctx)

    def signin_get(self):
        # サインアップ時と同様、エラーメッセージがあれば取り出して表示
        error_text = session.pop(session_name_signin_error, None)
        return render_template('signin.html', error_text=error_text)

    def signin_post(self):
        d = request.form
        text_id = d.get('text_id')
        password = d.get('password')

        # 1. ユーザーをDBから探す (ID または Email でログイン可能にするのが一般的)
        user = Known_Person.query.filter_by(text_id=text_id).first() # ID で探す。

        # 2. ユーザーが存在し、かつパスワードが一致するか検証
        if user and check_password_hash(user.password, password):
            # 認証成功！セッションに刻む
            session.clear() # セキュリティのため一度クリア
            session['user_id'] = user.id
            session['user_name'] = user.name
            
            # ホーム画面（またはマイページ）へリダイレクト
            return redirect(url_for('portal.index'))
        
        # 3. 認証失敗（ID間違いかPW間違いかはあえて明示しないのがセキュリティの定石）
        session[session_name_signin_error] = "ユーザIDまたはパスワードが正しくありません。"
        return redirect(url_for('facemans.signin_get'))

    def signout_get(self):
        session.clear() # これでセッションを空にする
        return redirect(url_for('portal.index'))

    def register(self, bp):
        # signup
        bp.add_url_rule('/signup', view_func=self.signup_get,  methods=['GET'],  endpoint='signup_get')
        bp.add_url_rule('/signup', view_func=self.signup_post, methods=['POST'], endpoint='signup_post')
        # signin
        bp.add_url_rule('/signin', view_func=self.signin_get,  methods=['GET'],  endpoint='signin_get')
        bp.add_url_rule('/signin', view_func=self.signin_post, methods=['POST'], endpoint='signin_post')
        # signout
        bp.add_url_rule('/signout', view_func=self.signout_get, methods=['GET'],  endpoint='signout_get')
