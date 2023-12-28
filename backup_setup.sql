/* 创建备份账号*/

CREATE USER 'backup'@'%' IDENTIFIED BY 'password';
GRANT SELECT, SHOW VIEW, RELOAD, PROCESS, FILE, SUPER, LOCK TABLES ON *.* TO 'backup'@'%';
FLUSH PRIVILEGES;

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


/* 创建上报库账号*/

CREATE USER 'backup_reporting'@'%' IDENTIFIED BY 'password';
GRANT INSERT, UPDATE ON alart_history.dbs_backup_info TO 'backup_reporting'@'%';
FLUSH PRIVILEGES;
