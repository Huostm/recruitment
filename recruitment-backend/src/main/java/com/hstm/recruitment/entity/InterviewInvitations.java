package com.hstm.recruitment.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * @Author: zhangyuanfang
 * @CreateTime: 2026-09-04
 * @Description: 面试邀约表对应实体类
 */

@Data
public class InterviewInvitations {
    @TableId(type= IdType.AUTO)
    private Long id;

    private Long candidateId;
    private String emailSubject;
    private String emailBody;
    private LocalDateTime sentAt;
    private String status;

}
