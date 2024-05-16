#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : config.py.py
@Author     : LeeCQ
@Date-Time  : 2023/7/1 13:01
"""
import logging
import urllib.parse
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class BookCss:
    BOOK_NAME: str
    BOOK_AUTHOR: str
    BOOK_LIST: str
    BOOK_CONTENT: str
    BOOK_LIST_NEXT: str = None
    BOOK_CONTENT_NEXT: str = None

    @abstractmethod
    def book_id(self, url):
        pass

    @abstractmethod
    def chapter_id(self, url):
        pass

    @abstractmethod
    def page_id(self, url):
        pass


class BookCssBiququ(BookCss):
    def book_id(self, url):
        return url.split('/')[-2]

    def chapter_id(self, url):
        return url.split('/')[-1].split('.')[0]

    def page_id(self, url):
        return 1


class BookCssQushu(BookCss):
    def book_id(self, url):
        path = urllib.parse.urlsplit(url).path
        return path.split('/')[-2]

    def chapter_id(self, url):
        path = urllib.parse.urlsplit(url).path
        return path.split('/')[-1].split('.')[0].split('_')[1]

    def page_id(self, url):
        try:
            path = urllib.parse.urlsplit(url).path
            return path.split('/')[-1].split('.')[0].split('_')[2]
        except IndexError:
            return 1


DOMAIN_CONFIGS = {
    "www.biququ.la": {
        'class': BookCssBiququ,
        "BOOK_NAME": "#info > h1",
        "BOOK_AUTHOR": "#info > p:nth-child(2)",
        "BOOK_LIST": "#list > dl > dd > a",
        "BOOK_CONTENT": "#content",
    },
    "qushu.org": {
        "class": BookCssQushu,
        "BOOK_NAME": "body > div.container.autoheight > div.list-chapter > h1 > a",
        "BOOK_AUTHOR": "body > div.container.autoheight > div.list-chapter > h2 > a:nth-child(2)",
        "BOOK_LIST": "body > div.container.autoheight > div.list-chapter > div.booklist > ul > li > a",
        "BOOK_LIST_NEXT": "body > div.container.autoheight > div.list-chapter > div.booklist > div:nth-child(2) > span.right > a",
        "BOOK_CONTENT": "#chaptercontent",
        "BOOK_CONTENT_NEXT": "#chaptercontent > p > a",
    }
}


def config_finder(url: str) -> BookCss:
    url_split = urllib.parse.urlsplit(url)
    domain = url_split.netloc

    DOMAIN_CONFIG = DOMAIN_CONFIGS.get(domain, {})
    if not DOMAIN_CONFIG:
        raise Exception(f"未找到{domain}的配置")

    _class = DOMAIN_CONFIG.pop('class')

    return _class(**DOMAIN_CONFIG)


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    # "filters": {},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "down_book.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "encoding": "utf-8"
        },

    },
    "loggers": {
        "gh-actions": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file"],
    },

}
