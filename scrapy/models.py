#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : models.py
@Author     : LeeCQ
@Date-Time  : 2024/8/26 19:55
"""
from peewee import *


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase('scrapy.db')


class Book(BaseModel):
    idd: str = CharField()
    url: str = CharField(unique=True)
    title: str = CharField()
    body: str = TextField()
