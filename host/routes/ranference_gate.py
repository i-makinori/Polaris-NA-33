# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import select
from models import Tolopica, Ranference, Known_Person

class RanferenceGate:
    def __init__(self, config, db_session):
        self.config = config
        self.db = db_session

    def ranference_post(self, tolopica_text_id):
        """特定の板への書き込み処理"""
        # 0. check the exists of the ToLopica.
        tolopica = self.db.query(Tolopica).filter_by(text_id=tolopica_text_id).first()
        if not tolopica:
            flash("投稿先の板が見つかりません。")
            return redirect(url_for('tolopica.tolopica_list'))

        # 0. get Form Datas
        content = request.form.get('content', '').strip()
        faceman_type = request.form.get('faceman_type') # "faceless" or "faceman"
        coding_type = request.form.get('coding_type') # "text" or "markdown"

        # 1. Validations

        # 1.1 Content (thread's Text) check
        errors = []
        if not content:
            errors += ["内容を入力してください。"]
        if len(content) > 4000: # 掲示板としての常識的な制限
            errors += ["内容が長すぎます（4000文字以内）。"]
        # if len(content) < 10:
        # errors += ["内容が短かすぎます(10文字以上)。"]

        # 1.2 faceman_type check
        if not(faceman_type in ['faceless', 'faceman']): # どれでもない値（不正なリクエストなど）が送られてきた場合
            errors += ["投稿種別が正しくありません。"]

        # 1.3 coding_type check
        if not(coding_type in ['text', 'markdown']): # どれでもない値（不正なリクエストなど）が送られてきた場合
            errors += ["coding_type が不正です。"]

        # 1.R
        if errors:
            # エラーがある場合は、板の個別ページ（tolopica_show）に戻す
            return render_template('tolopica_show.html', topic=tolopica, error=errors, form_content=content)

        # 2. 投稿データの作成

        # 2.1 書き込みユーザの設定
        current_user_id = session.get('user_id') # Signinしているか?
        # ボタンが 'faceman' かつ Signinしていれば、 ID を紐付ける
        if faceman_type == 'faceman' and current_user_id:
            effective_author_id = current_user_id
        else:
            # それ以外（'faceless' ボタン、またはSigninしていない）はすべて 名無しさん
            effective_author_id = None

        # 2.2 投稿内容の設定
        new_ranference = Ranference(
            content=content,
            tolopica_id=tolopica.id,
            faceman_id=effective_author_id,
            coding_type=coding_type,
        )

        # 3. DB 書き込み
        try:
            self.db.add(new_ranference)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            # print(f"Post Error: {e}")
            flash("投稿に失敗しました。サーバーエラーです。")

        # 4. render and back to its tolopica
        flash("投稿しました。")
        return redirect(url_for('tolopica.tolopica_show', text_id=tolopica_text_id))


    def register(self, bp):
        # 投稿処理 (特定の板 text_id に対して POST)
        bp.add_url_rule('/tolopica/<tolopica_text_id>/post', view_func=self.ranference_post,
                        methods=['POST'], endpoint='ranference_post')
