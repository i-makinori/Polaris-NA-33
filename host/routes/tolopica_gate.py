# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import select, exists
from utils import logger_text, get_values_from_dict, GateABC
from models import Tolopica
from validation_text_input import is_bad_tolopica_id_text_p, is_bad_tolopica_title_text_p


# Routes defined in TolopicaGate

class TolopicaGate(GateABC):
    def register(self, bp):
        # share methods and endpoints
        bp.add_url_rule('/tolopica_add', view_func=self.tolopica_add_get,  methods=['GET'],  endpoint='tolopica_add_get')
        bp.add_url_rule('/tolopica_add', view_func=self.tolopica_add_post, methods=['POST'], endpoint='tolopica_add_post')

        bp.add_url_rule('/tolopica/', view_func=self.tolopica_list, endpoint='tolopica_list')

        # URL Rule with variables
        bp.add_url_rule('/tolopica/<text_id>', view_func=self.tolopica_show, endpoint='tolopica_show')

    @staticmethod
    def _tolopica_add_post_errors(c_Tolopica, text_id, title):
        """
        板作成時のバリデーションを集約
        """
        # 0. 必須チェック
        if not (text_id and title):
            return ["全ての項目を入力してください。"]

        # 1. 各フィールドの文字列形式チェック（地雷リストの結合）
        errors = []
        errors += is_bad_tolopica_id_text_p(text_id)
        errors += is_bad_tolopica_title_text_p(title)

        # 2. DB重複チェック
        if c_Tolopica.query.filter_by(text_id=text_id).first():
            errors.append("この板IDは既に登録されています。")

        # R. return
        return errors


    def tolopica_add_get(self):
        """板の新規作成 (フォーム)"""
        return render_template('tolopica_add.html')

    def tolopica_add_post(self):
        """板の新規作成 (DB書き込み) そして、 フォームなどへとリダイレクト """
        # 1. variables setting. (and also getting from POST).
        # 1.1 handle posted datas
        keys = ['text_id', 'title']
        text_id, title_raw = get_values_from_dict(request.form, keys)
        # title, = map(str.strip, [title_raw]) # a[0] object # white_spaces for title_text is detected in validation.
        title = title_raw
        ctx = {'form_text_id': text_id, 'form_title': title}

        # 2. Validations
        errors = self._tolopica_add_post_errors(Tolopica, text_id, title)
        # 2.R if some errors, return with error message
        if errors != [] :
            return render_template('tolopica_add.html', **ctx, error=errors)

        # 3. new_topic の鋳型の作成
        new_topic = Tolopica(text_id=text_id, title=title)

        # 4. write to DB (maybe exceptions)
        db_success_p = self.safe_db_write(
            self.db, self.logger, new_topic,
            log_tag="DB_ERROR_TOLOPICA_POST",
            context=ctx,
        )

        # 5. case by db_success_p
        if not db_success_p:
            # 5.R render
            error_messages_to_client = ["板の作成に失敗しました。サーバエラーです。"]
            return render_template('tolopica_add.html', error=error_messages_to_client, **ctx)
        else:
            # 5.R render with flash message
            flash(f"新しい板「{title}」を作成しました。")
            return redirect(url_for('tolopica.tolopica_list'))


    def tolopica_list(self):
        """板の一覧表示"""
        # 作成日時順に並び替えて全取得
        topics = self.db.execute(
            select(Tolopica).order_by(Tolopica.created_at.desc())
        ).scalars().all()
        return render_template('tolopica_list.html', topics=topics)

    def tolopica_show(self, text_id):
        """個別の板の表示（スレッド一覧など）"""
        topic = self.db.execute(
            select(Tolopica).filter_by(text_id=text_id)
        ).scalar_one_or_none()

        if not topic:
            return "Topic not found", 404

        return render_template('tolopica_show.html', topic=topic)



