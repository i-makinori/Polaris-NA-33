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
