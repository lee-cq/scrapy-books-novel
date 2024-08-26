#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : down_book.py
@Author     : LeeCQ
@Date-Time  : 2023/5/7 19:15
"""
import asyncio
import json
import logging
import os
import sys
import threading
import time
import re
from collections import defaultdict
from pathlib import Path
from queue import Queue as _Queue, Empty

import pymysql
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException, \
    WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from sqllib.common.error import SqlWriteError
from sqllib import MySqlAPI, SQLiteAPI, BaseSQLAPI

from chrome import chrome
from replace import replace, replace_from_sql
from config import config_finder

logger = logging.getLogger("scrapy.down_book")


def is_url(url) -> bool:
    """判断是否为URL"""
    if url is None:
        return False
    return re.match(r'^https?://', url) is not None


class Queue(_Queue):

    def get_all(self):
        """获取队列中所有的数据"""
        try:
            while True:
                yield self.get_nowait()
        except Empty:
            pass


class DownTxt:
    sql: BaseSQLAPI = None
    book_name: str = None

    def __init__(self, url, _sql=None):
        self.url = url
        logger.info('Download URL: %s' % url)
        self.browser = chrome(
            executable_path=r"C:\Programma\bin\chromedriver.exe",
            use_js=False,
            pic=False,
            notification=False,
            # is_headless=True,
            ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35'
        )
        self.browser.set_window_size(800, 600)
        self.set_sql(_sql)  # 设置数据库
        self.body_queue = Queue()  # 正文列队，批量演示写入数据库
        self.cache_dict = defaultdict(str)  # 缓存字典, 用于分页的章节
        self.have_new_tab = True  # 是否还有未下载的章节
        self.have_new_body = True  # 是否还有未写入数据库的正文
        self.domain_config = config_finder(url) if url else None

    def set_sql(self, _sql: BaseSQLAPI = None):
        if _sql:
            self.sql = _sql
            return
        self.sql = SQLiteAPI('cache/down_txt.db')

    def create_table(self):
        """创建数据库"""
        if not self.book_name:
            raise Exception('请先获取书籍名称')
        _c = (f"CREATE TABLE IF NOT EXISTS `{self.book_name}` ( "
              f"_id      INT(10)     NOT NULL    PRIMARY KEY AUTO_INCREMENT, "
              f"idd     INT(10)    , "
              f"url     VARCHAR(255)     NOT NULL   , "
              f"title   VARCHAR(512), "
              f"body    TEXT"
              f" ) ")
        return self.sql.write_db(_c)

    def verify_bot(self):
        """验证机器人"""
        logger.info('验证机器人')
        self.browser.implicitly_wait(10)
        while True:
            if self.browser.title != 'Just a moment...':
                break
            time.sleep(1)
            self.browser.switch_to.frame(
                self.browser.find_elements(By.TAG_NAME, "iframe")[0])
            ActionChains(self.browser).move_by_offset(60, 300).click().perform()
            ActionChains(self.browser).move_to_element(
                self.browser.find_element(By.CSS_SELECTOR,
                                          '#recaptcha-anchor')).click().perform()
            self.browser.find_element(By.CSS_SELECTOR, '#verifying').click()
        logger.info('验证完成')

    def find_list(self):
        """获取章节列表"""
        next_url = self.url
        while True:
            try:
                if not is_url(next_url):
                    break
                self.browser.get(next_url)
                self.browser.implicitly_wait(10)
                for item in self.browser.find_elements(
                        By.CSS_SELECTOR,
                        self.domain_config.BOOK_LIST):
                    yield item.get_attribute('href'), item.text
                if self.domain_config.BOOK_LIST_NEXT:
                    next_url = self.browser.find_element(
                        By.CSS_SELECTOR,
                        self.domain_config.BOOK_LIST_NEXT
                    ).get_attribute('href')
                else:
                    break
            except NoSuchElementException or WebDriverException:
                logger.info('分页结束')
                break
        yield "END", "END"

    # noinspection PyProtectedMember
    def create_metadata(self):
        """获取URL头"""
        self.browser.get(self.url)
        self.browser.implicitly_wait(10)
        if self.browser.title == 'Just a moment...':
            logger.warning('需要验证')
            self.verify_bot()
        self.book_name = f"{self.browser.find_element(By.CSS_SELECTOR, self.domain_config.BOOK_AUTHOR).text.replace(' ', '').replace('作者：', '')}-" \
                         f"{self.browser.find_element(By.CSS_SELECTOR, self.domain_config.BOOK_NAME).text}-" \
                         f"{time.strftime('%Y%m', time.localtime())}"
        self.create_table()
        logger.info('Book Name: %s', self.book_name)

        url_s = [x[0] for x in self.sql.read_db(f"SELECT url FROM `{self.book_name}`")]
        logger.info('已经写入的章节信息数量: %d' % len(url_s))

        if 'END' in url_s:
            logger.info('元数据信息初始化 - 已经完成')
            return

        cursor = self.sql._sql.cursor()

        for _url, _name in self.find_list():
            if _url in url_s:
                continue
            idd = self.domain_config.chapter_id(_url) if _url != "END" else 0
            logger.info(f'创建元数据章节：{idd} {_name}, {_url}')
            cursor.execute(
                f"INSERT INTO `{self.book_name}` (idd, url, title) VALUES ( '{idd}', '{_url}', '{_name}')", )

        self.sql._sql.commit()
        logger.info('元数据信息初始化 - 完成')

    def opened_tabs(self):
        """打开标签页"""

        def _opened_url(cu) -> str:
            self.browser.switch_to.window(cu)
            return self.browser.current_url

        return [_opened_url(i) for i in self.browser.window_handles]

    async def open_tab(self):
        """异步打开标签页"""

        urls = self.sql.read_db(
            f"SELECT url FROM `{self.book_name}` WHERE body IS NULL and url != \"END\""
        )

        if not urls:
            logger.info('全部Body下载完成 ...')
            self.have_new_tab = False
            return

        logger.info('未下载的章节数量: %d' % len(urls))

        for i, url in enumerate(urls):
            url = url[0]
            while len(self.browser.window_handles) >= 15 + 1:
                await asyncio.sleep(0.01)
            if url in self.opened_tabs():
                continue
            logger.info('Will Open %d %s' % (i, url))

            self.browser.switch_to.window(self.browser.window_handles[0])
            self.browser.execute_script(f'window.open("{url}","_blank");')

        self.body_queue.join()  # 等待列队中的数据全部写入数据库
        while len(self.browser.window_handles) > 1:
            await asyncio.sleep(0.01)
        await self.open_tab()  # 递归检查是否还有未下载的章节

    async def get_body(self, chapter_window):
        """获取正文"""

        while self.have_new_tab:
            await asyncio.sleep(0.001)
            for i in self.browser.window_handles:
                await asyncio.sleep(0.001)
                if i == chapter_window:
                    continue
                try:
                    self.browser.switch_to.window(i)
                    if self.browser.title == 'Just a moment...':
                        logger.warning('需要验证')
                        self.verify_bot()
                        continue

                    self.browser.implicitly_wait(0.1)
                    _body = '\n'.join(
                        i.text for i in self.browser.find_elements(
                            By.CSS_SELECTOR,
                            self.domain_config.BOOK_CONTENT)
                    )

                    if _body:
                        idd = self.domain_config.chapter_id(self.browser.current_url)
                        page_id = self.domain_config.page_id(self.browser.current_url)
                        logger.info(
                            f'获取正文成功：{self.browser.title}_{page_id} '
                            f'长度：{len(_body)}'
                        )

                        if self.domain_config.BOOK_CONTENT_NEXT:  # 有分页
                            self.cache_dict[idd] += _body + '\n'
                            try:
                                self.browser.implicitly_wait(0.1)
                                next_url = self.browser.find_element(
                                    By.CSS_SELECTOR,
                                    self.domain_config.BOOK_CONTENT_NEXT
                                ).get_attribute('href')
                            except NoSuchElementException:
                                next_url = None

                            if is_url(next_url) and idd in next_url and int(page_id) <= 10:
                                logger.info(f'分页: {next_url}')
                                self.browser.execute_script(
                                    f'window.open("{next_url}","_blank");')
                                self.browser.close()
                                continue
                            else:
                                logger.info(f'分页结束: {self.browser.title}')
                                self.body_queue.put((
                                    idd,
                                    replace(self.cache_dict.pop(idd)),
                                ))
                                self.browser.close()

                        else:  # 无分页
                            self.body_queue.put((idd, replace(_body)))
                            self.browser.close()
                    else:
                        logger.error(f'获取正文失败：{self.browser.title}')
                except (NoSuchWindowException, NoSuchElementException) as _e:
                    logger.info(f'EE: {type(_e)}')
                    continue
        else:
            logger.info('获取正文完成 ...')
            self.have_new_body = False

        logger.warning('结束获取正文 但是 Body 写入队列未完成 ...')

    def write_body_sql(self):
        """写入正文到数据库"""

        while True:
            if self.have_new_body is False:
                logger.info('数据写入完成 ...')
                break
            all_queue = []
            try:
                all_queue = [dict(u=u, b=b) for u, b in
                             self.body_queue.get_all()]  # i: (url, body)
                if not all_queue:
                    logger.debug("等待写入正文 ...")
                    time.sleep(3)
                    continue
                logger.info('从列队中获取正文: %d', len(all_queue))
                # print(all_queue)
                _rows = self.sql.write_rows(
                    f"UPDATE `{self.book_name}` SET body=%(b)s WHERE idd=%(u)s",
                    all_queue
                )
                self.body_queue.task_done()
                logger.info(
                    '写入正文成功：影响 %d 行, (Body列队长度: %d, Cache Body长度： %d) %s',
                    _rows,
                    self.body_queue.qsize(),
                    len(self.cache_dict),
                    ", ".join(str(len(b["b"])) for b in all_queue)
                )
            except (pymysql.err.ProgrammingError, SqlWriteError) as _e:
                logger.warning(f"SQL 写入失败: {_e}, args: {all_queue}")

    def async_write_body(self):
        """"""
        chapter_window = self.browser.window_handles[0]

        async def main():
            await asyncio.gather(
                self.open_tab(),
                self.get_body(chapter_window),
            )

        _w = threading.Thread(target=self.write_body_sql, daemon=True)
        _w.start()
        asyncio.run(main())
        logger.info('Async Loop Done ...')
        _w.join()
        self.browser.quit()

    @property
    def save_path(self) -> Path:
        return Path() / 'cache' / f'{self.book_name}.txt'

    # 合并为txt
    def merge_txt(self):
        """合并为txt"""
        logger.info('合并为txt')
        _body = '\n\n'.join(
            f'{t}\n{b}' for t, b in self.sql.read_db(
                f"SELECT title, body FROM `{self.book_name}`"
            ))
        self.save_path.write_text(_body, encoding='gb18030')
        logger.info('合并为txt完成')

    def github_env(self):
        if os.getenv('GITHUB_ENV'):
            logger.info('写入环境变量到 GITHUB_ENV')
            with open(os.getenv('GITHUB_ENV'), 'a', encoding='utf-8') as f:
                f.write(f"BOOK_NAME={self.book_name}.txt\n")
                f.write(f"BOOK_PATH={self.save_path.absolute()}\n")
        else:
            logger.warning('未配置 GITHUB_ENV')

    def replace_from_sql(self):
        logger.info('开始清理SQL Body中的广告 ...')
        return replace_from_sql(self.sql, self.book_name)


def init_sql(sql_connect=None):
    # load_dotenv(Path(__file__).parent / '.env')
    if sql_connect is None:
        try:
            mysql_info = json.loads(os.getenv('MYSQL_INFO'))
            sql_connect = MySqlAPI(
                **mysql_info,
                charset='gb18030',
                use_unicode=True,
                pool=True,
            )
            logger.info('使用mysql, Host: %s' % mysql_info['host'])
        except Exception as _e:
            logger.warning('未配置数据库或配置错误，使用sqlite： {_e}', exc_info=True)
    return sql_connect


def down_txt(url, sql_connect=None):
    """下载小说"""
    if sql_connect is None:
        sql_connect = init_sql()
    a = DownTxt(url)
    a.set_sql(sql_connect)
    a.create_metadata()
    a.async_write_body()
    if os.getenv('REPLACE_FROM_SQL', False):
        a.replace_from_sql()
    a.merge_txt()
    a.github_env()


def replace_sql(table_name, sql_connect=None):
    """"""
    if sql_connect is None:
        sql_connect = init_sql()
    a = DownTxt('')
    a.set_sql(sql_connect)
    a.book_name = table_name
    a.replace_from_sql()
    a.merge_txt()


if __name__ == '__main__':
    import logging.config
    from config import LOG_CONFIG

    logging.config.dictConfig(LOG_CONFIG)

    if load_dotenv(Path(__file__).parent / '.env'):
        logger.info('加载环境变量成功')

    DOWNLOAD_LINK = sys.argv[1] if len(sys.argv) > 1 else os.getenv('DOWNLOAD_LINK', )
    DOWNLOAD_NAME = os.getenv('DOWNLOAD_NAME', '')
    REPLACE_NAME = os.getenv('REPLACE_NAME', '')

    logger.info('DOWNLOAD_LINK: %s' % DOWNLOAD_LINK)

    down_txt(DOWNLOAD_LINK)
    # replace_sql(REPLACE_NAME)
