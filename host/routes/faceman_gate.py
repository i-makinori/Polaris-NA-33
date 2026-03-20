# -*- coding: utf-8 -*-
from flask import flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
#
from utils import logger_text, get_values_from_dict, GateABC
from models import Known_Person
from validation_text_input import is_bad_faceman_name_text_p, is_bad_email_text_p, is_bad_faceman_id_text_p, is_bad_password_text_p

# Routes defined in FacemanGate

class FacemanGate(GateABC):
    def register(self, bp):
        # signup
        bp.add_url_rule('/signup', view_func=self.signup_get,  methods=['GET'],  endpoint='signup_get')
        bp.add_url_rule('/signup', view_func=self.signup_post, methods=['POST'], endpoint='signup_post')
        # signin
        bp.add_url_rule('/signin', view_func=self.signin_get,  methods=['GET'],  endpoint='signin_get')
        bp.add_url_rule('/signin', view_func=self.signin_post, methods=['POST'], endpoint='signin_post')
        # signout
        bp.add_url_rule('/signout', view_func=self.signout_get, methods=['GET'],  endpoint='signout_get')

    @staticmethod
    def _signup_post_errors(c_Known_Person, name, text_id, email, p1, p2):
        """
        全てのバリデーションを実行し、エラーメッセージのリストを返す。
        DB照合などの「外部への副作用」を伴うチェックもここに集約する。
        """
        # 0. 必須項目チェック（ガード節）
        if not (name and text_id and email and p1 and p2):
            return ["全項目を入力して下さい。"]

        # 1. 各フィールドの文字列形式チェック（地雷リストの結合）
        errors = []
        errors += is_bad_faceman_name_text_p(name)
        errors += is_bad_faceman_id_text_p(text_id)
        errors += is_bad_email_text_p(email)
        errors += is_bad_password_text_p(p1, p2)

        # 2. DB重複チェック
        if c_Known_Person.query.filter_by(text_id=text_id).first():
            errors.append("このユーザIDは既に使用されています。別のIDをお試しください。")
        if c_Known_Person.query.filter_by(email=email).first():
            errors.append("このメールアドレスは既に登録されています。")

        # R. return
        return errors


    def signup_get(self):
        return render_template('signup.html')

    def signup_post(self):
        # 1. variables setting. (and also getting from POST).
        # 1.1 handle posted datas
        keys = ('name', 'text_id', 'email', 'password_1', 'password_2')
        name_raw, text_id_raw, email_raw, p1, p2 = get_values_from_dict(request.form, keys)
        name, text_id, email = map(str.strip, [name_raw, text_id_raw, email_raw])

        ctx = {'form_name': name, 'form_text_id': text_id, 'form_email': email}

        # 2. Validations
        errors = self._signup_post_errors(Known_Person, name, text_id, email, p1, p2)
        # 2.R. if some errors, return with error message.
        if errors != [] :
            return render_template('signup.html', error=errors, **ctx)
        # if p1 != p2 :
        #     return render_template('signup.html', error=["パスワードが一致しません。"], **ctx)

        # 3 new_user の鋳型の作成
        hash_pass = generate_password_hash(p1) # assume p1 == p2
        new_user = Known_Person(name=name, email=email, text_id=text_id, password=hash_pass)

        # 4 DB write (maybe exceptions)
        db_success_p = self.safe_db_write(
            new_user,
            log_tag="DB_ERROR_SIGNUP",
            context= ctx | {"p_1":"...omit...", "p2":"...omit..."}, # appended dict
        )

        # 5. case by db_success_p
        # 5.F if Fail ...
        if not db_success_p:
            # 5.R render
            error_messages_to_client = ["ユーザ登録に失敗しました。サーバエラーです。"]
            return render_template('signup.html', error=error_messages_to_client, **ctx)
        # 5.T if Success ...
        else:
            # 5.1 signin at client
            self.state_signin(text_id, p1)

            # # 5.2 write server's log file
            # log_context = {"name": name, "text_id": text_id, "email": email, "p_1":"...omit...", "p2":"...omit...",}
            # log_msg = logger_text("SIGNUP_DB_MESSAGE", context=log_context)
            # self.logger.info(log_msg, exc_info=False) # not in exception

            # 5.2 update context (ctx)
            ctx |= { # append
                'tml_message' : f"{name}さんは、id: {text_id} かつ、 email: {email} にてユーザ登録されました。",
                'tml_title' : "ユーザ登録完了"
            }
            # 5.R render
            return render_template('message.html', **ctx)

    def signin_get(self):
        return render_template('signin.html')

    def signin_post(self):
        keys = ['text_id', 'password']
        text_id, password = get_values_from_dict(request.form, keys)

        # 認証
        detect_signin = self.state_signin(text_id, password)
        # 画面表示
        if detect_signin==True: # 認証成功
            flash("ログインしました。")
            return redirect(url_for('portal.index', ))
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
