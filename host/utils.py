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
    return [ (data_dict.get(k) or default).strip() for k in key_list ]


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

    # def safe_db_write(self, model_obj, error_msg="Server Error", log_tag="DB_ERR", context=None):
    #     """
    #     DBへの add/commit/rollback とエラーログ出力を一元化。
    #     """
    #     try:
    #         self.db.add(model_obj)
    #         self.db.commit()
    #         return True, None
    #     except Exception as e:
    #         self.db.rollback()
    #         log_content = logger_text(log_tag, context={**(context or {}), "error": str(e)})
    #         self.logger.error(log_content, exc_info=True)
    #         return False, error_msg
