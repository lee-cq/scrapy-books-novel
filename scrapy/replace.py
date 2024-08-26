#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : replace.py
@Author     : LeeCQ
@Date-Time  : 2023/5/11 13:05
"""
import re
import logging

from sqllib import BaseSQLAPI

logger = logging.getLogger("scrapy.down-txt.replace")

REMOVE_TEXT = r"""
《一周只更新一章，绝大部分时间写仙剑之星月神话，同时抽点时间续写斗破小天地，说真的，写了也白写，你们觉得精彩的话，等隔段时间请你们帮忙多加收藏仙剑之星月神话吧，恩，写仙剑去了。》
【.*?换源App.*?】
<br/*>
br>
起点手游《吞噬星空》新区火爆 起点币月票ipadmini天天送 官网 tsxk\.qidian\.com（未完待续）
起点中文网www.欢迎广大书友光临阅读，最新、最快、最火的连载作品尽在起点原创！
番茄推荐一本好书《宦海风月》，历史架空类的，很不错啊，地址：http://www\./Book/1623706\.aspx
[\(（\[【].*?qidian\.com.*?[\)）\]】]
章节报错
热门推荐：.*$
求推荐票，求收藏！
求推荐票，求收藏！谢谢大家！
本章未完，请点击下一页继续阅读！.*$
咱们情节推进了……推荐票是不是也往前推进一下，收藏一下，就是对老鱼的支持
求票，继续求推荐，求收藏！谢谢大家！
，最快更新校花的贴身高手最新章节！
推荐收藏支持老鱼，谢谢各位
^……………………$
求推荐票求收藏召唤啊召唤老鱼拜谢
…*?正文…*?
看清爽的小说就到【 】
精华书阁 www.axs6.com，最快更新.*?最新章节！
紧急通知：精华书阁启用新地址-www.axs6.com，请重新收藏书签！
为您提供.*?最快更新，为了您下次还能查看到本书的最快更新，请务必保存好书签！
第\d+章 .*?免费阅读.https://www.axs6.com
\(本章未完，请点击下一页继续阅读\)
"""

REPLACE_DICT = {
    '丢shi': '丢失',
    'xian': '现',
    'xiao': '小',
    'xue': '雪',
    'xun': '寻',
    'xuan': '玄',
    'yan': '眼',
    'se': '色',
    "\n\n\n\n": "\n",
    "\n\n\n": "\n",
}

__all__ = ['replace', 'replace_from_sql']


def replace(s: str) -> str:
    # remove
    s = re.sub(r'\n+', '\n', s, flags=re.IGNORECASE)
    for line in REMOVE_TEXT.split('\n'):
        _s = s
        s = re.sub(line, '', s, flags=re.IGNORECASE)
        if _s != s:
            logger.debug('Removed: %s', line)
    # replace
    for k, v in REPLACE_DICT.items():
        _s = s
        s = re.sub(k, v, s)
        if _s != s:
            logger.debug('Removed: %s', k)
    return s


def replace_from_sql(sql: BaseSQLAPI, table: str = None):
    """从数据库中读取数据并替换"""

    if table:
        tables = [table]
    else:
        tables = [t[0] for t in sql.show_tables() if t[0] not in [
            'sqlite_sequence', 'FD_Books', 'FD_Books_v2', 'FDT_Books', 'FDT_Books_v2',
            'FDT_Books_v3'
        ]
                  ]

    logger.info(f'Replace tables: {tables}')
    for _t in tables:
        logger.info(f'Replace tables: {_t}')
        try:
            offset = 0
            while True:
                logger.info('正在加载数据, offset: %s', offset)
                logger.info(
                    f'SQL: select title, body from `{_t}` where body IS NOT NULL LIMIT 100 OFFSET {offset}')
                _lines = sql.read_db(
                    f'select title, body from `{_t}` where body IS NOT NULL LIMIT 100 OFFSET {offset}')
                offset += 100
                if not _lines:
                    logger.info(f'Replace tables: {_t} done')
                    break
                for title, body in _lines:
                    new_body = replace(body)
                    if body == new_body:
                        # logger.info(f'{title} No change. continue.')
                        continue
                    logger.info(f'Replace {_t} {title}')
                    sql.write_db(
                        f"update `{_t}` set body='{new_body}' where title='{title}'")
        except Exception as _e:
            logger.warning('Exception: type %s, msg: %s', type(_e), _e)
            continue
    else:
        logger.info('Replace all done.')
