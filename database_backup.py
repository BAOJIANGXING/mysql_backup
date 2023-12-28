#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : database_backup.py
# @Author: bjxing
# @Date  : 2023/12/28
# @Desc  : 备份类

import os
import time
import pymysql
import gzip
import bisect
import subprocess
import math
from configparser import ConfigParser
from datetime import datetime
from os import path
from sshtunnel import SSHTunnelForwarder
from args_parser import get_config_file

config_file = get_config_file()
config = ConfigParser()
cfg = config.read(config_file, encoding='utf-8')


class DatabaseBackup(object):
    def __init__(self, section, logger):
        self.logger = logger.debug
        self.mysql_dump_path = path.abspath(path.join(path.dirname(__file__), 'bin/mysqldump'))
        self.mysql_project = config.get(section, 'project')
        self.mysql_host = config.get(section, 'host')
        self.mysql_port = config.get(section, 'port')
        self.mysql_user = config.get(section, 'user')
        self.mysql_password = config.get(section, 'password')
        self.mysql_socket = config.get(section, 'mysql_sock')
        self.target_databases = config.get(section, 'target_dbs').split(',')
        self.backup_directory = config.get('Default',
                                           'back_path') + self.mysql_host + ":" + self.mysql_port + '/' + time.strftime(
            "%Y%m%d")
        self.retention_time = int((config.get('Default', 'retention_time'))) * 24 * 60 * 60
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.bksize = None
        self.bkstate = None
        self.proxy_host = config.get('Proxy_Server', 'proxy_host')
        self.proxy_port = config.get('Proxy_Server', 'proxy_port')
        self.proxy_username = config.get('Proxy_Server', 'proxy_username')
        self.proxy_password = config.get('Proxy_Server', 'proxy_password')
        self.local_port = config.get('Proxy_Server', 'local_port')
        self.report_host = config.get('Info_Reporting', 'host')
        self.report_port = config.get('Info_Reporting', 'port')
        self.report_user = config.get('Info_Reporting', 'user')
        self.report_password = config.get('Info_Reporting', 'password')

    def perform_backup(self, db_name):
        try:
            self.logger(f"开始执行备份任务: {db_name}")
            self.start_time = time.time()
            if not (os.path.exists(self.backup_directory)):
                os.makedirs(self.backup_directory)
                self.logger("备份目录不存在，创建目录" + self.backup_directory)
            sql_file = self.backup_directory + "/" + db_name + '_' + time.strftime("%Y%m%d%H%M%S") + ".sql"
            self.logger(f"正在连接数据库{self.mysql_host}:{self.mysql_port}，开始执行备份{db_name}")
            command = "%s -h%s -P%s -u%s -p%s -S %s --single-transaction --skip-lock-tables --ssl-mode=DISABLE %s > %s" % \
                      (self.mysql_dump_path, self.mysql_host, self.mysql_port, self.mysql_user, self.mysql_password,
                       self.mysql_socket, db_name, sql_file)
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                                    universal_newlines=True)
            self.logger(f"[{command}] 标准错误输出: {result.stderr}")
            if os.path.exists(sql_file):
                gzip_file = sql_file + '.gz'
                with open(sql_file, 'rb') as f_in:
                    with gzip.open(gzip_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(sql_file)
                fsize = os.path.getsize(gzip_file)
                self.bksize = self.format_filesize(fsize)
                self.bkstate = 1
                self.logger(f"执行gzip压缩命令，备份文件 {gzip_file}， 大小{self.bksize}")
        except Exception as e:
            self.logger(f"执行失败: {str(e)}")
            self.bksize = 0
            self.bkstate = 0
            self.logger(f"***备份任务 {db_name} 执行失败!!!***")
        finally:
            self.end_time = time.time()
            self.elapsed_time = self.format_time(math.ceil(self.end_time - self.start_time))
            self.logger(f"备份任务 {db_name} 执行完毕，耗时: {self.elapsed_time}")
            if int(config.get('Info_Reporting', 'report_enabled')) == 1:
                self.backup_info_reporting(db_name)
            else:
                self.logger(f"备份信息上报已被关闭，请在配置中开启。")
        return self.start_time, self.end_time, self.elapsed_time, self.bksize, self.bkstate

    def query_databases(self):
        conn = pymysql.connect(
            host=self.mysql_host,
            port=int(self.mysql_port),
            user=self.mysql_user,
            passwd=self.mysql_password,
            db='mysql',
        )
        cur = conn.cursor()
        cur.execute('show databases')
        data = cur.fetchall()
        return data

    def format_filesize(self, size):
        d = [(1024 - 1, 'K'), (1024 ** 2 - 1, 'M'), (1024 ** 3 - 1, 'G'), (1024 ** 4 - 1, 'T')]
        s = [x[0] for x in d]
        index = bisect.bisect_left(s, size) - 1
        if index == -1:
            return str(size) + 'B'
        else:
            b, u = d[index]
        return str(round(size / (b + 1), 1)) + u

    def format_time(self, size):
        d = [(60 - 1, '分钟'), (3600 - 1, '小时')]
        s = [x[0] for x in d]
        index = bisect.bisect_left(s, size) - 1
        if index == -1:
            return str(size) + '秒'
        else:
            b, u = d[index]
        return str(round(size / (b + 1), 1)) + u

    def clean_old_backups(self, section):
        if not self.retention_time:
            self.logger(f"未设置备份保留时长，请手动回收备份文件。")
        else:
            del_time = time.strftime("%Y%m%d", time.gmtime(time.time() - self.retention_time))
            root_backup_directory = config.get('Default', 'back_path') + self.mysql_host + ":" + self.mysql_port + '/'
            for root, directories, files in os.walk(root_backup_directory):
                for directory in directories:
                    if directory < del_time:
                        directory_to_delete = root_backup_directory + directory
                        result = subprocess.run(['rm', '-rf', directory_to_delete], stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE, text=True)
                        if result.returncode == 0:
                            self.logger(
                                f"删除数据库{self.mysql_host}:{self.mysql_port}的备份文件{del_time}前的数据，文件{directory_to_delete}删除成功。")
                        else:
                            self.logger(
                                f"删除数据库{self.mysql_host}:{self.mysql_port}的备份文件{del_time}前的数据失败，标准错误：{result.stderr}")

    def backup_info_reporting(self, dbname):
        self.server = None
        self.db_host = None
        self.db_port = None
        try:
            if int(config.get('Proxy_Server', 'proxy_enabled')) == 1:
                self.logger(f"已开启数据上报代理模式！")
                self.server = SSHTunnelForwarder(
                    ssh_address_or_host=(self.proxy_host, int(self.proxy_port)),
                    ssh_username=self.proxy_username,
                    ssh_password=self.proxy_password,
                    remote_bind_address=(self.report_host, int(self.report_port)),
                    local_bind_address=('127.0.0.1', int(self.local_port)),
                )
                self.server.start()
                self.server.check_tunnels()
                # print(self.server.tunnel_is_up, flush=True)
                if self.server.is_active:
                    self.logger(
                        '本地端口:{}已转发至远程端口{}:{}'.format(self.server.local_bind_port, self.proxy_host, self.proxy_port))
                else:
                    self.logger('本地端口{}:{}转发失败,请重试')

                self.db_host = self.server.local_bind_host
                self.db_port = self.server.local_bind_port
            else:
                self.logger(f"未开启数据上报代理模式！")
                self.db_host = self.report_host
                self.db_port = int(self.report_port)

            conn = pymysql.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.report_user,
                passwd=self.report_password,
                db=config.get('Info_Reporting', 'db'),
            )
            insert_sql = "INSERT INTO dbs_backup_info(project, source, category, address, port, dbname, " \
                         "bksize, bktype, bkstate, start_time, end_time, elapsed_time) " \
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            params = (
                self.mysql_project, 'IDC', 'Mysql', self.mysql_host, self.mysql_port, dbname, self.bksize, '全量',
                self.bkstate, self.convert_timestamp_to_datetime(self.start_time),
                self.convert_timestamp_to_datetime(self.end_time), self.elapsed_time)
            cur = conn.cursor()
            cur.execute(insert_sql, params)
            conn.commit()
            formatted_sql = cur.mogrify(insert_sql, params)
            self.logger(f"执行数据上报{self.report_host}，插入语句： {formatted_sql}")
            cur.close()
            conn.close()
            if int(config.get('Proxy_Server', 'proxy_enabled')) == 1:
                self.server.stop()
            return 'successful'
        except Exception as e:
            self.logger(f"备份信息上报时发生异常: {str(e)}")
            return 'failed'

    def convert_timestamp_to_datetime(self, timestamp):
        formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
