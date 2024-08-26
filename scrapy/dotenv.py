#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File Name  : dotenv.py
@Author     : LeeCQ
@Date-Time  : 2024/8/25 23:47
"""

import os


def load_dotenv(dotenv_path, encoding='utf-8'):
    for line in open(dotenv_path, 'r', encoding=encoding):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        k, v = line.split('=', 1)
        os.environ[k] = v
        print(f"load {k}={v}")
