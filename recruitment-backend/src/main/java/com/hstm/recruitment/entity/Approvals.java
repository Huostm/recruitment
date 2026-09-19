package com.hstm.recruitment.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

/**
 * @Author: recruitment-system
 * @Description: 人工审批记录表
 */
@TableName("approvals")
@Data
public class Approvals {
    @TableId(type = IdType.AUTO)
    private Long id;

    private Long candidateId;

    private String approver;

    private String decision;

    private String reason;

    @TableField(fill = FieldFill.INSERT)
    private Date approvedAt;
}
