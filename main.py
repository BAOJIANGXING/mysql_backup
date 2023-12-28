#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : main.py
# @Author: bjxing
# @Date  : 2023/12/20
# @Desc  : 主代码


import os
import sys

from configparser import ConfigParser
from database_backup import DatabaseBackup
from logger_config import setup_logger
from args_parser import get_config_file

logger = setup_logger()
config_file = get_config_file()
config = ConfigParser()
config.read(config_file, encoding='utf-8')

if __name__ == "__main__":
    # print(f"版本1.1： 支持数据上报代理模式，备份主机无法上网时使用。")
    try:
        for section in config.sections():
            if section.startswith('DB'):
                backup_instance = DatabaseBackup(section, logger)
                try:
                    if len(config.get(section, 'target_dbs')) == 0:
                        data = backup_instance.query_databases()
                        for db_names in data:
                            for db_name in db_names:
                                if db_name == 'information_schema' or db_name == 'performance_schema' or \
                                        db_name == 'mysql' or db_name == 'sys':
                                    continue
                                backup_instance.perform_backup(db_name)
                    else:
                        dbs = config.get(section, 'target_dbs').split(',')
                        for db_name in dbs:
                            backup_instance.perform_backup(db_name)
                except Exception as e:
                    logger.exception("备份任务执行出现异常：%s", str(e))
                    continue

                backup_instance.clean_old_backups(section)

    except Exception as e:
        logger.exception("备份任务执行出现异常：%s", str(e))
