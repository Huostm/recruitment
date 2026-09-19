package com.hstm.recruitment.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.hstm.recruitment.dto.CandidateDetailResponse;
import com.hstm.recruitment.entity.Approvals;
import com.hstm.recruitment.entity.Candidates;
import com.hstm.recruitment.entity.InterviewInvitations;
import com.hstm.recruitment.mapper.ApprovalsMapper;
import com.hstm.recruitment.mapper.CandidatesMapper;
import com.hstm.recruitment.mapper.InterviewInvitationsMapper;
import com.hstm.recruitment.service.AgentService;
import com.hstm.recruitment.service.CandidatesService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * @Author: recruitment-system
 * @Description: 候选人服务实现
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class CandidatesServiceImpl extends ServiceImpl<CandidatesMapper, Candidates> implements CandidatesService {

    private final AgentService agentService;
    private final ApprovalsMapper approvalsMapper;
    private final InterviewInvitationsMapper interviewInvitationsMapper;
    private final JavaMailSender mailSender;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> processResume(MultipartFile file) {
        log.info("开始处理简历上传");

        try {
            // 1. 验证文件类型
            if (file.isEmpty()) {
                throw new RuntimeException("文件不能为空");
            }
            String filename = file.getOriginalFilename();
            if (filename == null || !filename.toLowerCase().endsWith(".pdf")) {
                throw new RuntimeException("只支持 PDF 文件");
            }

            // 2. 提取 PDF 文本
            String resumeText = extractTextFromPDF(file);
            log.info("PDF 文本提取完成，长度: {}", resumeText.length());

            // 3. 调用 Agent 1 解析简历
            Map<String, Object> parseResult = agentService.parseResume(resumeText);

            if (!(Boolean) parseResult.get("success")) {
                throw new RuntimeException("简历解析失败: " + parseResult.get("error"));
            }

            Map<String, Object> parsedData = (Map<String, Object>) parseResult.get("data");

            // 4. 从解析结果中提取基本信息
            String name = parsedData.get("name") != null ? parsedData.get("name").toString() : "未知";
            String email = parsedData.get("email") != null ? parsedData.get("email").toString() : null;
            String phone = parsedData.get("phone") != null ? parsedData.get("phone").toString() : null;

            log.info("解析出的候选人信息: name={}, email={}, phone={}", name, email, phone);

            // 5. 调用 Agent 2 进行 JD 匹配
            Map<String, Object> matchResult = agentService.matchJD(parsedData);

            if (!(Boolean) matchResult.get("success")) {
                throw new RuntimeException("JD 匹配失败: " + matchResult.get("message"));
            }

            Map<String, Object> matchData = (Map<String, Object>) matchResult.get("data");

            // Agent 2 匹配结果
            Object scoreObj = matchData.get("match_score");
            BigDecimal matchScore = scoreObj instanceof Number
                    ? BigDecimal.valueOf(((Number) scoreObj).doubleValue())
                    : new BigDecimal(scoreObj.toString());

            // 6. 调用 Agent 3 进行深度评估
            Map<String, Object> evaluateResult = agentService.evaluate(parsedData, matchData);

            if (!(Boolean) evaluateResult.get("success")) {
                throw new RuntimeException("深度评估失败: " + evaluateResult.get("message"));
            }

            Map<String, Object> evaluationData = (Map<String, Object>) evaluateResult.get("data");

            // 7. 保存到数据库
            Candidates candidate = new Candidates();
            candidate.setName(name);
            candidate.setEmail(email);
            candidate.setPhone(phone);
            candidate.setResumeText(resumeText);
            candidate.setEducation(parsedData.get("education"));
            candidate.setSkills(parsedData.get("skills"));
            candidate.setExperience(parsedData.get("experience"));
            candidate.setParsedData(parsedData);

            // Agent 2 匹配结果
            candidate.setMatchScore(matchScore);
            candidate.setMatchDetails(matchData);

            // Agent 3 评估结果
            Object evalScoreObj = evaluationData.get("overall_score");
            BigDecimal evaluationScore = evalScoreObj instanceof Number
                    ? BigDecimal.valueOf(((Number) evalScoreObj).doubleValue())
                    : new BigDecimal(evalScoreObj.toString());
            candidate.setEvaluationScore(evaluationScore);
            candidate.setEvaluationResult(evaluationData);

            // 使用 Agent 3 的最终状态
            String status = evaluationData.get("status") != null
                    ? evaluationData.get("status").toString()
                    : "pending";
            candidate.setStatus(status);

            log.info("Agent 3 评估完成，综合得分: {}，状态: {}", evaluationScore, status);

            // 手动设置时间戳
            Date now = new Date();
            candidate.setCreatedAt(now);
            candidate.setUpdatedAt(now);

            this.save(candidate);
            log.info("候选人保存成功，ID: {}", candidate.getId());

            // 如果状态是 approved，自动发送面试邀请
            if ("approved".equals(status)) {
                sendInterviewInvitation(candidate.getId(), null, null);
                log.info("候选人 {} 状态为 approved，已自动发送面试邀请", candidate.getId());
            }

            // 8. 返回结果
            Map<String, Object> result = new HashMap<>();
            result.put("candidate_id", candidate.getId());
            result.put("name", name);
            result.put("match_score", matchScore);
            result.put("evaluation_score", candidate.getEvaluationScore());
            result.put("status", candidate.getStatus());
            return result;

        } catch (Exception e) {
            log.error("简历处理失败", e);
            throw new RuntimeException("简历处理失败: " + e.getMessage());
        }
    }

    /**
     * 从 PDF 文件提取文本
     */
    private String extractTextFromPDF(MultipartFile file) throws IOException {
        try (PDDocument document = PDDocument.load(file.getInputStream())) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    @Override
    public CandidateDetailResponse getCandidateDetail(Long id) {
        Candidates candidate = this.getById(id);
        if (candidate == null) {
            throw new RuntimeException("候选人不存在");
        }

        CandidateDetailResponse response = new CandidateDetailResponse();
        response.setId(candidate.getId());
        response.setName(candidate.getName());
        response.setEmail(candidate.getEmail());
        response.setPhone(candidate.getPhone());
        response.setEducation(candidate.getEducation());
        response.setSkills(candidate.getSkills());
        response.setExperience(candidate.getExperience());
        response.setMatchScore(candidate.getMatchScore());
        response.setMatchDetails(candidate.getMatchDetails());
        response.setStatus(candidate.getStatus());
        response.setCreatedAt(candidate.getCreatedAt());
        response.setUpdatedAt(candidate.getUpdatedAt());

        return response;
    }

    @Override
    public Map<String, Object> getCandidateList(Integer page, Integer size, String status) {
        Page<Candidates> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Candidates> queryWrapper = new LambdaQueryWrapper<>();

        if (status != null && !status.isEmpty()) {
            queryWrapper.eq(Candidates::getStatus, status);
        }

        queryWrapper.orderByDesc(Candidates::getCreatedAt);

        Page<Candidates> result = this.page(pageObj, queryWrapper);

        List<CandidateDetailResponse> records = result.getRecords().stream()
                .map(candidate -> {
                    CandidateDetailResponse response = new CandidateDetailResponse();
                    response.setId(candidate.getId());
                    response.setName(candidate.getName());
                    response.setEmail(candidate.getEmail());
                    response.setPhone(candidate.getPhone());
                    response.setEducation(candidate.getEducation());
                    response.setSkills(candidate.getSkills());
                    response.setExperience(candidate.getExperience());
                    response.setMatchScore(candidate.getMatchScore());
                    response.setMatchDetails(candidate.getMatchDetails());
                    response.setStatus(candidate.getStatus());
                    response.setCreatedAt(candidate.getCreatedAt());
                    response.setUpdatedAt(candidate.getUpdatedAt());
                    return response;
                })
                .collect(Collectors.toList());

        Map<String, Object> response = new HashMap<>();
        response.put("records", records);
        response.put("total", result.getTotal());
        response.put("page", result.getCurrent());
        response.put("size", result.getSize());

        return response;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void approveCandidate(Long id, String decision, String reason) {
        Candidates candidate = this.getById(id);
        if (candidate == null) {
            throw new RuntimeException("候选人不存在");
        }

        if (!"approved".equals(decision) && !"rejected".equals(decision)) {
            throw new RuntimeException("decision 必须是 approved 或 rejected");
        }

        // 更新候选人状态
        candidate.setStatus(decision);
        this.updateById(candidate);

        // 保存审批记录到 approvals 表
        Approvals approval = new Approvals();
        approval.setCandidateId(id);
        approval.setApprover("system"); // 可以从登录用户获取
        approval.setDecision(decision);
        approval.setReason(reason);
        approval.setApprovedAt(new Date());
        approvalsMapper.insert(approval);

        log.info("候选人 {} 审批完成，结果: {}, 原因: ", id, decision, reason);

        // 如果通过审批，自动发送面试邀请
        if ("approved".equals(decision)) {
            sendInterviewInvitation(id, null, null);
            log.info("候选人 {} 已自动发送面试邀请", id);
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void sendInterviewInvitation(Long id, String interviewTime, String location) {
        Candidates candidate = this.getById(id);
        if (candidate == null) {
            throw new RuntimeException("候选人不存在");
        }

        if (!"approved".equals(candidate.getStatus())) {
            throw new RuntimeException("只有已通过的候选人才能发送面试邀请");
        }

        // 构建邮件内容
        String emailSubject = "面试邀请 - " + candidate.getName();
        String emailBody = String.format(
                "尊敬的 %s：\n\n" +
                "恭喜您通过了简历筛选！请点击以下链接查看面试详情：\n\n" +
                "www.baidu.com\n\n" +
                "祝好！\nHR 团队",
                candidate.getName()
        );

        // 保存面试邀请记录
        InterviewInvitations invitation = new InterviewInvitations();
        invitation.setCandidateId(id);
        invitation.setEmailSubject(emailSubject);
        invitation.setEmailBody(emailBody);
        invitation.setRecipientEmail("2172948307@qq.com");
        invitation.setSentAt(new Date());
        invitation.setStatus("sent");
        interviewInvitationsMapper.insert(invitation);

        // 真正发送邮件
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom("2172948307@qq.com");
            message.setTo("2172948307@qq.com");
            message.setSubject(emailSubject);
            message.setText(emailBody);
            mailSender.send(message);
            log.info("面试邀请邮件已发送给候选人 {}, 接收邮箱: 2172948307@qq.com", id);
        } catch (Exception e) {
            log.error("邮件发送失败: ", e);
            throw new RuntimeException("邮件发送失败: " + e.getMessage());
        }
    }

    @Override
    public Map<String, Object> getStatistics() {
        // 按 email 或 phone 去重统计
        // 获取所有候选人
        List<Candidates> allCandidates = this.list();

        // 按 email 或 phone 去重（保留最新记录）
        Map<String, Candidates> uniqueMap = new HashMap<>();
        for (Candidates candidate : allCandidates) {
            String key = candidate.getEmail() != null ? candidate.getEmail() : candidate.getPhone();
            if (key != null) {
                Candidates existing = uniqueMap.get(key);
                if (existing == null || candidate.getCreatedAt().after(existing.getCreatedAt())) {
                    uniqueMap.put(key, candidate);
                }
            }
        }

        // 统计去重后的各状态数量
        long totalCount = uniqueMap.size();
        long approvedCount = uniqueMap.values().stream()
                .filter(c -> "approved".equals(c.getStatus())).count();
        long pendingCount = uniqueMap.values().stream()
                .filter(c -> "pending".equals(c.getStatus())).count();
        long rejectedCount = uniqueMap.values().stream()
                .filter(c -> "rejected".equals(c.getStatus())).count();

        Map<String, Object> stats = new HashMap<>();
        stats.put("total", totalCount);
        stats.put("approved", approvedCount);
        stats.put("pending", pendingCount);
        stats.put("rejected", rejectedCount);

        log.info("统计数据（去重后）: total={}, approved={}, pending={}, rejected={}",
                totalCount, approvedCount, pendingCount, rejectedCount);

        return stats;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void rescueCandidate(Long id, String reason) {
        Candidates candidate = this.getById(id);
        if (candidate == null) {
            throw new RuntimeException("候选人不存在");
        }

        if (!"rejected".equals(candidate.getStatus())) {
            throw new RuntimeException("只有已拒绝的候选人才能捞回");
        }

        // 更新状态为 pending
        candidate.setStatus("pending");
        this.updateById(candidate);

        // 保存捞回记录到 approvals 表
        Approvals approval = new Approvals();
        approval.setCandidateId(id);
        approval.setApprover("system");
        approval.setDecision("rescue");
        approval.setReason(reason);
        approval.setApprovedAt(new Date());
        approvalsMapper.insert(approval);

        log.info("候选人 {} 已捞回，原因: {}", id, reason);
    }
}
