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
 * @Description: 候选人表对应实体类
 */

@Data
@TableName(autoResultMap = true)
public class Candidates {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;
    private String email;
    private String phone;
    private String resumeText;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> education;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String,Object> skills;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> experience;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> parsedData;

    private BigDecimal matchScore;

    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> evaluationResult;

    private String status;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

}
