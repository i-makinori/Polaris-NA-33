import datetime



def logger_text(message, level="ERROR", context=None):
    """
    context: 記録したい変数などの辞書 {'name': name, 'email': email, ...}
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 辞書の中身を文字列に変換
    ctx_str = " | ".join([f"{k}={v}" for k, v in context.items()]) if context else "None"
    
    return f"[{timestamp}] [{level}] {message} >> Context: {ctx_str}"
