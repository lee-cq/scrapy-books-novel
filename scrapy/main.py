#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : main.py.py
@Author     : LeeCQ
@Date-Time  : 2023/5/29 21:04
"""
import logging.config
from pathlib import Path

from dotenv import load_dotenv

from down_book import down_txt

logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'log.txt',
                'formatter': 'standard'
            },
        },
        "loggers": {
            "scrapy": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
            },
            "sqllib": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
            },
        }
    }
)

load_dotenv(Path(__file__).parent / '.env')
down_txt("https://www.axs6.com/126163/")
