package com.hstm.recruitment.entity;
import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.ser.std.ToStringSerializer;
import com.hstm.recruitment.handler.JsonbTypeHandler;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.Map;

/**
 * @Author: zhangyuanfang
 * @CreateTime: 2026-09-04
 * @Description: 候选人表对应实体类
 */

@TableName(value ="candidates")
@Data
public class Candidates {
    /**
     * 主键ID
     */
    @TableId
    @JsonSerialize(using = ToStringSerializer.class)
    private Long id;

    /**
     * 候选人姓名
     */
    private String name;

    /**
     * 邮箱
     */
    private String email;

    /**
     * 电话
     */
    private String phone;

    /**
     * 简历原文
     */
    private String resumeText;

    /**
     * 教育背景 {"school": "", "major": "", "degree": ""}
     */
    @TableField(typeHandler = JsonbTypeHandler.class)
    private Object education;

    /**
     * 技能 {"languages": [], "frameworks": [], "databases": [], ...}
     */
    @TableField(typeHandler = JsonbTypeHandler.class)
    private Object skills;

    /**
     * 项目经验 [{"name": "", "description": "", "tech_stack": [], ...}]
     */
    @TableField(typeHandler = JsonbTypeHandler.class)
    private Object experience;

    /**
     * Agent 1 完整解析结果（保留原始输出）
     */
    @TableField(typeHandler = JsonbTypeHandler.class)
    private Object parsedData;

    /**
     * JD 匹配分数（0-100），Agent 2 输出
     */
    private BigDecimal matchScore;

    /**
     * Agent 2 匹配详情 {"skill_score": 85, "education_score": 75, "experience_score": 80, "top_jd_chunks": [...]}
     */
    @TableField(typeHandler = JsonbTypeHandler.class)
    private Object matchDetails;

    /**
     * 综合评估分数（0-100），Agent 3 输出
     */
    private BigDecimal evaluationScore;

    /**
     * Agent 3 完整评估结果
     */
    @TableField(typeHandler = JsonbTypeHandler.class)
    private Object evaluationResult;

    /**
     * 状态: approved(≥70自动通过), pending(50-70待审核), rejected(<50淘汰但可捞回)
     */
    private String status;

    /**
     * 创建时间
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private Date createdAt;

    /**
     * 更新时间
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private Date updatedAt;
}