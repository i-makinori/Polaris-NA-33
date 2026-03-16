# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 1. 接続用インスタンスの箱を準備
# models.py で db を定義し、server.py で後から紐付ける（Flask-SQLAlchemyの作法）
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# 2. モデル定義の基底クラス
class Base(DeclarativeBase):
    pass

class Tolopica(db.Model):
    __tablename__ = 'tolopica'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uri: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    ranferences: Mapped[List["Ranference"]] = relationship(back_populates="tolopica")

class Ranference(db.Model):
    __tablename__ = 'ranference'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    tolopica_id: Mapped[int] = mapped_column(ForeignKey('tolopica.id'))
    faceman_id: Mapped[Optional[int]] = mapped_column(ForeignKey('known_person.id'), nullable=True)
    
    tolopica: Mapped["Tolopica"] = relationship(back_populates="ranferences")
    author: Mapped[Optional["Known_Person"]] = relationship(back_populates="ranferences")

class Known_Person(db.Model):
    __tablename__ = 'known_person'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    
    ranferences: Mapped[List["Ranference"]] = relationship(back_populates="author")

class Post(db.Model):
    __tablename__ = 'post'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
