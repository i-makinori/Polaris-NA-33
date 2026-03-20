# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import select, exists
from utils import GateABC
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


    def tolopica_add_get(self):
        """板の新規作成 (フォーム)"""
        return render_template('tolopica_add.html')

    def tolopica_add_post(self):
        """板の新規作成 (DB書き込み) そして、 フォームなどへとリダイレクト """

        text_id = request.form.get('text_id', '')
        title_d = request.form.get('title', '')
        ctx = {'form_text_id':text_id, 'form_title':title_d}

        # 1. Validate form datas
        errors = []
        # 1.1 text_id check
        errors += is_bad_tolopica_id_text_p

        ## DB collision
        stmt = exists().where(Tolopica.text_id == text_id)
        is_collision = self.db.query(stmt).scalar()
        if is_collision:
            errors += ["この板IDは既に登録されています。"]

        ## 1.2 title check
        errors += is_bad_tolopica_title_text_p

        # 1.R if some errors, return with error message
        if errors != [] :
            return render_template('tolopica_add.html', **ctx, error=errors)

        # 2. new_topic の鋳型の作成
        title=title_d.strip() # 白字除去
        new_topic = Tolopica(text_id=text_id, title=title)

        # 3. write to DB
        try:
            self.db.add(new_topic)
            self.db.commit()
        except Exception as e:
            # ここでの rollback は「万が一」の保険。
            # 他のユーザーが同時に同じIDで commit した場合などに発動する。
            self.db.rollback()
            print(f"Ranference POST Error: {e}")
            errors += ["登録に失敗しました。サーバーエラーです。"]
            return render_template('tolopica_add.html', **ctx, error=errors) # exception page

        # render with flash message
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



