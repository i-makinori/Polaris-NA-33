import datetime



def logger_text(message, context=None):
    """
    message: message,
    context: 記録したい変数などの辞書 {'name': name, 'email': email, ...}
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if context:
        # 辞書の中身を文字列に変換
        ctx_str = " | ".join([f"{k}={v if v else '(empty)'}" for k, v in context.items()])
    else:
        # 辞書が無いならば、 "nothing" とする
        ctx_str = "nothing"

    return f"[{message}]\n>> Context: {ctx_str}\n"

