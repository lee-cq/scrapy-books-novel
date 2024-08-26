# scrapy-books-novel

爬取小说

## 环境准备

- Python 3.6+
- chromedriver

# 爬取配置

位置： `config.py`

重写 `config.BookCss` 类，实现自定义的 CSS 选择器，并将其添加到 `config.DOMAIN_CONFIGS`
字典中。

内容细节间`config.BookCss`

## TODO

- [] 数据库存储使用peewee
