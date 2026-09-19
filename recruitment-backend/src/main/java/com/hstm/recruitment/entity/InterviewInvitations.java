package com.hstm.recruitment.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Date;

/**
 * @Author: zhangyuanfang
 * @CreateTime: 2026-09-04
 * @Description: 面试邀约表对应实体类
 */

@TableName(value ="interview_invitations")
@Data
public class InterviewInvitations {
    /**
     * 主键ID
     */
    @TableId
    private Long id;

    /**
     * 候选人ID（外键）
     */
    private Long candidateId;

    /**
     * 邮件主题
     */
    private String emailSubject;

    /**
     * 邮件正文
     */
    private String emailBody;

    /**
     * 发送时间
     */
    private Date sentAt;

    /**
     * 发送状态: pending(待发送), sent(已发送), failed(失败)
     */
    private String status;

    /**
     * 接收者邮箱
     */
    private String recipientEmail;
}
