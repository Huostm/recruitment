package com.hstm.recruitment.dto;

import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.ser.std.ToStringSerializer;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

/**
 * @Author: recruitment-system
 * @Description: 候选人详情响应
 */
@Data
public class CandidateDetailResponse {

    @JsonSerialize(using = ToStringSerializer.class)
    private Long id;

    private String name;

    private String email;

    private String phone;

    private Object education;

    private Object skills;

    private Object experience;

    private BigDecimal matchScore;

    private Object matchDetails;

    private BigDecimal evaluationScore;

    private String resumeText;

    private String status;

    private Date createdAt;

    private Date updatedAt;
}
