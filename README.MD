## Mysqlbackup

主要使用mysqldump实现批量的实例库进行备份，并支持数据上报。

## 版本 1.1.1
```bash
1、支持批量实例备份 
2、实例多库时可以为空，自动查找实例中的库进行全备 
3、支持数据上报 
4、支持数据上报代理模式 
5、增加参数解释说明
```

## 运行

### 创建信息上报库

```bash
/* 创建信息上报库 */
DROP TABLE IF EXISTS `dbs_backup_info`;
CREATE TABLE `dbs_backup_info`
(
    `id`           bigint(20)                         NOT NULL AUTO_INCREMENT,
    `project`      varchar(128) CHARACTER SET utf8mb4 NULL     DEFAULT NULL COMMENT '项目名称',
    `source`       varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '来源',
    `category`     varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '数据库类型',
    `address`      varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '数据库地址',
    `port`         varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '数据库端口',
    `dbname`       varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '数据库名',
    `bksize`       varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '备份大小',
    `bktype`       varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '备份类型',
    `bkstate`      varchar(32) CHARACTER SET utf8mb4  NULL     DEFAULT NULL COMMENT '备份状态',
    `start_time`   timestamp                          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    `end_time`     timestamp                          NULL COMMENT '结束时间',
    `elapsed_time` varchar(255) CHARACTER SET utf8mb4 NULL     DEFAULT NULL COMMENT '持续时间',

    PRIMARY KEY (`id`) USING BTREE,
    INDEX `start_time_index` (`start_time`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
```

### 创建上报库账号（可选）

```bash
/* 创建上报库账号*/
CREATE USER 'backup_reporting'@'%' IDENTIFIED BY 'password';
GRANT INSERT, UPDATE ON alart_history.dbs_backup_info TO 'backup_reporting'@'%';
FLUSH PRIVILEGES;
```

### 创建备份账号（可选）

```bash
/* 创建备份账号*/
CREATE USER 'backup'@'%' IDENTIFIED BY 'dRAnZDa4yvjR'; GRANT SELECT, SHOW VIEW, RELOAD, PROCESS, FILE, SUPER, LOCK
TABLES ON *.* TO 'backup'@'%'; FLUSH PRIVILEGES;
```

## 修改配置

config.ini中修改配置，多实例备份复制[DB1]配置，以DB开始，如DB1...DB10等

## 手动执行备份

1、使用python3解释器执行 
```bash
pip3 install -r requirements.txt 
python3 main.py
```

2、使用dist中可执行文件 
```bash
chmod +x mysqlbackup ./mysqlbackup
```

## 定时执行备份

例如： 每日一点进行备份 
```bash
crontab -e 
0 1 * * * cd /data/scripts/mysql_backup/&&./mysqlbackup
```

## 参数
```bash
-v 查看版本信息
-c 指定配置文件
```