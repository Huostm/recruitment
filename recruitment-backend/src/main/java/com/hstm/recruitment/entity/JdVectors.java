package com.hstm.recruitment.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * @Author: zhangyuanfang
 * @CreateTime: 2026-09-04
 * @Description: JD 岗位表对应实体类
 */

@Data
public class JdVectors {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String jdText;
    private String vectorId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
