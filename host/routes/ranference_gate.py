# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, session
from utils import logger_text, get_values_from_dict, GateABC
from sqlalchemy import select
from models import Tolopica, Ranference, Known_Person
# from validation_text_input import # Nothing


class RanferenceGate(GateABC):
    def register(self, bp):
        # 投稿処理 (特定の板 text_id に対して POST)
        bp.add_url_rule('/tolopica/<tolopica_text_id>/post', 
                        view_func=self.ranference_post,
                        methods=['POST'], 
                        endpoint='ranference_post')

    @staticmethod
    def _ranference_post_errors(c_Ranference, content, faceman_type, coding_type):
        """
        投稿内容、投稿種別、コーディングタイプのバリデーション。
        """
        errors = []
        
        # 1. コンテンツチェック
        if content!="" and content.strip()=="": # 「Whitespace 言語」への非対応を明示
            errors.append("「Whitespace_言語」には、対応していません。\\n")
            errors.append(" 「 」と「	」だけの宇宙宇宙な投稿には、対応していません。\\EOF")
        elif not content:
            errors.append("内容を入力してください。")
        elif len(content) > 4000:
            errors.append("内容が長すぎます（4000文字以内）。")

        # 2. 選択肢チェック (ホワイトリスト方式)
        if faceman_type not in ['faceless', 'faceman']:
            errors.append("投稿種別が正しくありません。")

        if coding_type not in ['text', 'markdown']:
            errors.append("コーディングタイプが不正です。")

        return errors

    def ranference_post(self, tolopica_text_id):
        """特定の板への書き込み処理"""
        # 0. check the existance of its Tolopica (Board) .(as guard condition)
        tolopica = self.db.query(Tolopica).filter_by(text_id=tolopica_text_id).first()
        if not tolopica:
            flash("投稿先の板が見つかりません。")
            return redirect(url_for('tolopica.tolopica_list'))

        # 1. variables setting. (and also getting from POST).
        # 1.1 handle posted datas
        keys = ('content', 'faceman_type', 'coding_type')
        content_raw, faceman_type, coding_type = get_values_from_dict(request.form, keys)
        # content = content_raw.strip() if content_raw else ""
        content = content_raw # handle whitespace (but maybe client get error_message of whitespace_error)

        ctx = {'topic': tolopica, 'form_content': content, 'form_coding_type': coding_type}

        # 2. Validation
        errors = self._ranference_post_errors(None ,content, faceman_type, coding_type) # None maybe Ranference
        # 2.R. if some errors, return with error message.
        if errors:
            return render_template('tolopica_show.html', error=errors, **ctx)

        # 3 Ranference (投稿データ)  の鋳型の作成
        # 3.1 著者IDの決定 (Signin状態 & faceman選択時のみ IDを紐付け)
        current_user_id = session.get('user_id') # ??? これで所持できる?

        is_faceman_post = (faceman_type == 'faceman' and current_user_id)
        effective_author_id = current_user_id if is_faceman_post else None

        # 3.2 モデルのインスタンス化
        new_ranference = Ranference(content=content,
                                    tolopica_id=tolopica.id, faceman_id=effective_author_id,
                                    coding_type=coding_type,)

        # 4. DB書き込み (抽象クラスの共通メソッドを利用)
        db_success_p = self.safe_db_write(
            self.db, self.logger, new_ranference,
            log_tag="DB_ERROR_RANFERENCE_POST",
            context=ctx | {"author_id": effective_author_id}
        )

        # 5. 結果に応じたレスポンス
        if not db_success_p:
            errors_to_client = ["投稿に失敗しました。サーバーエラーです。"]
            return render_template('tolopica_show.html', error=errors_to_client, **ctx)

        # 6. 成功時の処理
        flash("投稿しました。")
        return redirect(url_for('tolopica.tolopica_show', text_id=tolopica_text_id))
