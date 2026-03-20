# -*- coding: utf-8 -*-
#
# text Validations for input texts

import re


# Utility for some validations.
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


# register regrep as constant for processing speed
RE_DIGIT = re.compile(r'\d')
RE_ALPHA = re.compile(r'[a-zA-Z]')
RE_EMAIL = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
RE_FACEMAN_ID_FORMAT = re.compile(r'^[a-zA-Z0-9_-]+$')

# constant words
RESERVED_WORDS = {'admin', 'root', 'system', 'config', 'guest', 'signup', 'signin', 'login'}


# validations
def is_bad_email_text_p(email):
    return validate_val_by_rules(
        email == "", "メールアドレスを入力してください。",
        [(RE_EMAIL.match(email) is None, "メールアドレスの形式が正しくありません。"),
         ('..' in email, "ドットが連続しているアドレスは使用できません。"), # not を外しました
         (len(email) > 254, "メールアドレスが長すぎます。")
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

def is_bad_faceman_name_text_p(name):
    return validate_val_by_rules(
        name == "", "名前を入力してください。",
        [(not (1 <= len(name) <= 100), "名前は1文字以上100文字以内で入力してください。"),
         ('\n' in name or '\r' in name, "名前には改行を使用できません。"),
         (name.strip() == "", "名前は空白以外の文字を含めてください。")
        ])

def is_bad_faceman_id_text_p(id_text):
    return validate_val_by_rules(
        id_text == "", "ユーザIDを入力してください。",
        [(RE_FACEMAN_ID_FORMAT.match(id_text) is None, "IDには英数字、アンダースコア(_)、ハイフン(-)のみ使用可能です。"),
         (not (6 <= len(id_text) <= 100), "IDは6文字以上100文字以内で設定してください。"),
         (id_text.lower() in RESERVED_WORDS, "そのIDは登録されています。")
        ])

