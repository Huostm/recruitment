package com.hstm.recruitment.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @Author: recruitment-system
 * @Description: 简历上传请求
 */
@Data
public class ResumeUploadRequest {

    @NotBlank(message = "姓名不能为空")
    private String name;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    private String phone;

    @NotBlank(message = "简历内容不能为空")
    private String resumeText;
}
