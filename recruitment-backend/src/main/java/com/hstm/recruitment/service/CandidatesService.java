package com.hstm.recruitment.service;

import com.hstm.recruitment.dto.CandidateDetailResponse;
import com.hstm.recruitment.entity.Candidates;
import com.baomidou.mybatisplus.extension.service.IService;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

/**
* @author Administrator
* @description 针对表【candidates】的数据库操作Service
* @createDate 2026-09-04 12:20:20
*/
public interface CandidatesService extends IService<Candidates> {

    /**
     * 处理简历上传（PDF文件 -> 调用 Agent 1 + Agent 2）
     */
    Map<String, Object> processResume(MultipartFile file);

    /**
     * 获取候选人详情
     */
    CandidateDetailResponse getCandidateDetail(Long id);

    /**
     * 获取候选人列表（分页 + 状态筛选）
     */
    Map<String, Object> getCandidateList(Integer page, Integer size, String status);

    /**
     * 人工审批
     */
    void approveCandidate(Long id, String decision, String reason);

    /**
     * 发送面试邀请
     */
    void sendInterviewInvitation(Long id, String interviewTime, String location);

    /**
     * 获取统计数据
     */
    Map<String, Object> getStatistics();

    /**
     * 捞回候选人（rejected -> pending）
     */
    void rescueCandidate(Long id, String reason);
}
