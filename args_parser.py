#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : logger_config.py
# @Author: bjxing
# @Date  : 2023/12/28
# @Desc  : 参数解释和配置

import sys
import os
import argparse


def get_config_file():
    if args.config:
        return args.config
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'config.ini')


def print_version():
    print("当前版本：1.1.3 修复关闭代理模式时循环上报问题；去掉重试次数；增加--set-gtid-purged=OFF参数。")


parser = argparse.ArgumentParser(description='备份程序')
parser.add_argument('-c', '--config', help='指定配置文件路径')
parser.add_argument('-v', '--version', action='store_true', help='查看当前版本信息')
args = parser.parse_args()

if args.version:
    print_version()
    sys.exit()
