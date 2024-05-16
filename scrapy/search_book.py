#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : search_book.py
@Author     : LeeCQ
@Date-Time  : 2023/5/12 20:11
"""
from selenium.webdriver.common.by import By

from chrome import chrome

__all__ = ['search_book']


def search_book():
    """搜索书籍"""
    b = chrome()
    b.get('http://www.biququ.info/search.php')

    b.find_element(By.ID, 'searchkey').send_keys('诡秘之主')


if __name__ == '__main__':
    search_book()
