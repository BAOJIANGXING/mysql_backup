#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : logger_config.py
# @Author: bjxing
# @Date  : 2023/12/05
# @Desc  : 日志配置

import logging


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(pathname)s - %(lineno)d - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
