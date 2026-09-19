package com.hstm.recruitment.controller;

import com.hstm.recruitment.dto.CandidateDetailResponse;
import com.hstm.recruitment.dto.ResultVO;
import com.hstm.recruitment.service.CandidatesService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

/**
 * @Author: recruitment-system
 * @Description: 候选人管理接口
 */
@RestController
@RequestMapping("/api/candidates")
@RequiredArgsConstructor
public class CandidateController {

    private final CandidatesService candidatesService;

    /**
     * 上传简历（触发 Agent 1 + Agent 2）
     */
    @PostMapping("/upload")
    public ResultVO<Map<String, Object>> uploadResume(@RequestParam("file") MultipartFile file) {
        Map<String, Object> result = candidatesService.processResume(file);
        return ResultVO.success(result);
    }

    /**
     * 获取统计数据
     */
    @GetMapping("/statistics")
    public ResultVO<Map<String, Object>> getStatistics() {
        Map<String, Object> stats = candidatesService.getStatistics();
        return ResultVO.success(stats);
    }

    /**
     * 获取候选人详情（包含匹配详情）
     */
    @GetMapping("/{id}")
    public ResultVO<CandidateDetailResponse> getCandidateDetail(@PathVariable Long id) {
        CandidateDetailResponse response = candidatesService.getCandidateDetail(id);
        return ResultVO.success(response);
    }

    /**
     * 获取候选人列表（分页 + 状态筛选）
     */
    @GetMapping("/list")
    public ResultVO<Map<String, Object>> getCandidateList(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String status) {
        Map<String, Object> result = candidatesService.getCandidateList(page, size, status);
        return ResultVO.success(result);
    }

    /**
     * 人工审批（pending -> approved/rejected）
     */
    @PostMapping("/{id}/approve")
    public ResultVO<String> approveCandidate(
            @PathVariable Long id,
            @RequestBody Map<String, String> request) {
        candidatesService.approveCandidate(id, request.get("decision"), request.get("reason"));
        return ResultVO.success("审批成功");
    }

    /**
     * 发送面试邀请
     */
    @PostMapping("/{id}/invite")
    public ResultVO<String> sendInterview(
            @PathVariable Long id,
            @RequestBody Map<String, String> request) {
        candidatesService.sendInterviewInvitation(id, request.get("interviewTime"), request.get("location"));
        return ResultVO.success("面试邀请已发送");
    }

    /**
     * 捞回候选人（rejected -> pending）
     */
    @PostMapping("/{id}/rescue")
    public ResultVO<String> rescueCandidate(
            @PathVariable Long id,
            @RequestBody Map<String, String> request) {
        candidatesService.rescueCandidate(id, request.get("reason"));
        return ResultVO.success("候选人已捞回");
    }
}
