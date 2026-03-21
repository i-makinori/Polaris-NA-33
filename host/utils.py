# -*- coding: utf-8 -*-


# text format for logger
def logger_text(message, context=None, limit=100):
    """
    message: メッセージ
    context: 記録したい変数の辞書
    limit: 文字列を省略する閾値
    """
    def _abbreviate(v):
        s = str(v) if v is not None else "(empty)"
        s = s.replace('\n', ',\\n')
        t_len = len(s)
        if t_len > limit:
            h = (limit + 1) // 2
            return f"{s[:h]} ...[omit {t_len - limit} chars]... {s[-(limit-h):]}"
        return s

    if context:
        ctx_str = " | ".join([f"{k}={_abbreviate(v)}" for k, v in context.items()])
    else:
        ctx_str = "nothing"

    return f"[{message}]\n>> Context: {ctx_str}\n"


def get_values_from_dict(data_dict, key_list, default=""):
    """
    辞書（または辞書ライクなオブジェクト）から指定されたキーの値を一括取得し、
    Noneを回避して前後空白を削除したリストを返す。
    """
    # 1. get(k) が None なら default ("") を採用
    # 2. 文字列として .strip() を実行
    return [ (data_dict.get(k) or default) for k in key_list ]


# Abstract Base Class (ABC)
from abc import ABC, abstractmethod

## ABC of Gate Classes , used for Routing class such as HogehogeGate.
class GateABC(ABC):
    def __init__(self, config, db_session, logger):
        self.config = config
        self.db = db_session
        self.logger = logger

    @abstractmethod
    def register(self, bp):
        """Blueprintへのルーティング登録を強制する"""
        pass

    @staticmethod
    def safe_db_write(db_session, logger, model_obj, log_tag="DB_ERROR", context=None):
        """
        DBへの書き込みを試行し、失敗時はロールバックと詳細ログ出力を行う。
        引数に db_session と logger を取ることで副作用を排除。
        """
        try:
            db_session.add(model_obj)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()

            # write log to server logfile
            log_ctx = context.copy() if context else {}
            # e は exc_info=True によって詳細なスタックトレースとして出力されるため、log_ctxには加えない。
            log_msg = logger_text(log_tag, context=log_ctx)
            # logger も引数のものを使用
            logger.error(log_msg, exc_info=True)

            return False

    # user login status    def ensure_admin(self):
    def current_user(self):
        # request オブジェクト自体をキャッシュストレージとして使う
        #
        # request のデータは bp.add_url_rule された method が requestを受けた場合に、
        # return (または exception) した時点で破棄される。
        if not hasattr(request, '_cached_user_till_request'):
            user_id = session.get('user_id')
            request._cached_user_till_request = self.db.get(Known_Person, user_id) if user_id else None

        return request._cached_user_till_request


    # --- ガード関数 (ログイン状態の判定に依って、リクエスト処理を中断させる。) ---
    def ensure_login(self):
        """ログインしていなければ、リダイレクトオブジェクトを返す。
        呼び出し側で if res := self.ensure_login(): return res のように使う。
        """
        # プロパティとして呼び出す（キャッシュが効く）
        if self.current_user() is None:
            flash("この操作にはログインが必要です。")
            return redirect(url_for('faceman.signin_get'))
        return None

