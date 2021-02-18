CREATE TABLE IF NOT EXISTS `project`
(
    `string`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '字符串',
    `datetime` datetime DEFAULT NULL COMMENT '时间',
    `integer`  int(11)  DEFAULT 0 COMMENT '整数',
    PRIMARY KEY (`string`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '项目详情';