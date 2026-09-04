package com.hstm.recruitment.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * @Author: zhangyuanfang
 * @CreateTime: 2026-09-04
 * @Description: 人工审批表对应实体类
 */

@Data
public class Approvals {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long candidateId;
    private String approver;
    private String decision;
    private String reason;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime approvedAt;
}
