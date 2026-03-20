# -*- coding: utf-8 -*-


# text format for logger
def logger_text(message, context=None):
    """
    message: message,
    context: 記録したい変数などの辞書 {'name': name, 'email': email, ...}
    """
    if context:
        # 辞書の中身を文字列に変換
        ctx_str = " | ".join([f"{k}={v if v else '(empty)'}" for k, v in context.items()])
    else:
        # 辞書が無いならば、 "nothing" とする
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
