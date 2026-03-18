# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import select, exists
from models import Tolopica

# class Tolopica(db.Model):
#     __tablename__ = 'tolopica'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     text_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
#     title: Mapped[str] = mapped_column(String(100), nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
#
#     ranferences: Mapped[List["Ranference"]] = relationship(back_populates="tolopica")


#

import re

def is_ok_tolopica_text_id(text_id):
    """
    板のID (text_id) の健全性をチェック
    条件: 4-40文字, A-Za-z0-9, _, -
    """
    if not text_id:
        return False, "板のIDを入力してください。"
    # 1. 文字数チェック (1-120文字)
    if not (1 <= len(text_id) <= 120):
        return False, "板のIDは1文字以上120文字以内で設定してください。"
    # 2. 文字種チェック (regex)
    id_regex = r'^[a-zA-Z0-9_-]+$'
    if not re.match(id_regex, text_id):
        return False, "IDには英数字、アンダースコア(_)、ハイフン(-)のみ使用可能です。"
    # 3. 予約語チェック
    reserved = {'add', 'edit', 'delete', 'all', 'api'}
    if text_id.lower() in reserved:
        return False, "そのIDは使用されています。"
    return True, ""

def is_ok_tolopica_title(title):
    """
    板のタイトル (title) の健全性をチェック
    条件: 空白を除去して1文字以上
    """
    if not title:
        return False, "タイトルを入力してください。"
    # 左右の空白を除去
    stripped_title = title.strip()
    # 1. 空白除去後の文字数チェック (1文字以上)
    if len(stripped_title) < 1:
        return False, "タイトルは（空白を除いて）1文字以上入力してください。"
    # 2. 最大文字数チェック (ref: model.py の DB 定義 Tolopica title: ... String(*) ... に合わせる)
    if len(title) >= 100:
        return False, "タイトルが長すぎます（100文字未満に。）。"
    return True, ""

# Routes

class TolopicaGate:
    def __init__(self, config,db_session):
        self.config = config
        self.db = db_session

    def tolopica_add(self):
        """板の新規作成"""
        if request.method == 'GET':
            return render_template('tolopica_add.html')

        elif request.method == 'POST':
            text_id = request.form.get('text_id', '')
            title_d = request.form.get('title', '')

            # 1. Validate form datas
            # 1.1 text_id check
            ok_id, msg_id = is_ok_tolopica_text_id(text_id)
            if not ok_id:
                return render_template('tolopica_add.html', error=msg_id)

            ## DB collision
            stmt = exists().where(Tolopica.text_id == text_id)
            is_collision = self.db.query(stmt).scalar()

            if is_collision:
                return render_template('tolopica_add.html', error="この板IDは既に登録されています。")

            ## 1.2 title check
            ok_title, msg_title = is_ok_tolopica_title(title_d)
            if not ok_title:
                return render_template('tolopica_add.html', error=msg_title)

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
                # print(e)
                return render_template('tolopica_add.html', error="server error.")

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


    def register(self, bp):
        # share methods and endpoints
        bp.add_url_rule('/tolopica_add', view_func=self.tolopica_add, methods=['GET', 'POST'], endpoint='tolopica_add')

        bp.add_url_rule('/tolopica/', view_func=self.tolopica_list, endpoint='tolopica_list')
        
        # URL Rule with variables
        bp.add_url_rule('/tolopica/<text_id>', view_func=self.tolopica_show, endpoint='tolopica_show')





