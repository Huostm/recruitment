package com.hstm.recruitment.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Map;

/**
 * @Author: zhangyuanfang
 * @CreateTime: 2026-09-04
 * @Description: 匹配结果表对应实体类
 */

@Data
@TableName(autoResultMap = true)
public class MatchResults {
    @TableId(type = IdType.AUTO)
    private Long id;

    private Long candidateId;
    private Long jdId;
    private BigDecimal similarityScore;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> matchDetails;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
