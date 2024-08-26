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
    # 书籍名称
    BOOK_NAME: str
    # 书籍作者
    BOOK_AUTHOR: str
    # 书籍列表
    BOOK_LIST: str
    # 书籍内容
    BOOK_CONTENT: str
    # 书籍列表下一页
    BOOK_LIST_NEXT: str = None
    # 书籍内容下一页
    BOOK_CONTENT_NEXT: str = None

    @abstractmethod
    def book_id(self, url):
        """根据url获取书籍id"""
        pass

    @abstractmethod
    def chapter_id(self, url):
        """根据url获取章节ID， idd"""
        pass

    @abstractmethod
    def page_id(self, url):
        """根据url获取页面ID"""
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
        return path.split('/')[-1].split('.')[0].split('_')[0]

    def page_id(self, url):
        try:
            path = urllib.parse.urlsplit(url).path
            return path.split('/')[-1].split('.')[0].split('_')[1]
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
    },
    "www.jidewx.com": {
        'class': BookCssBiququ,
        "BOOK_NAME": "#info > h1",
        "BOOK_AUTHOR": "#info > p:nth-child(4)",
        "BOOK_LIST": "body > div.listmain > dl > dd > a",
        "BOOK_CONTENT": "#content",
    },
    "www.paozww.com": {
        'class': BookCssQushu,
    },
    "www.axs6.com": {
        "class": BookCssQushu,
        "BOOK_NAME": "#info > h1",
        "BOOK_AUTHOR": "#info > div > span:nth-child(1)",
        "BOOK_LIST": "#list > dl:nth-child(4) > dd > a",
        "BOOK_CONTENT": "#nr_content > p",
        "BOOK_CONTENT_NEXT": "#nexturl",
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
        "scrapy": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "sqllib": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file"],
    },
}
