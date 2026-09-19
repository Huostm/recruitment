package com.hstm.recruitment.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.Map;

/**
 * @Author: recruitment-system
 * @Description: Agent 服务调用
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class AgentService {

    private final WebClient.Builder webClientBuilder;

    @Value("${agent.service.url}")
    private String agentServiceUrl;

    /**
     * 调用 Agent 1: 简历解析
     */
    public Map<String, Object> parseResume(String resumeText) {
        log.info("调用 Agent 1 解析简历，文本长度: {}", resumeText.length());

        WebClient webClient = webClientBuilder.baseUrl(agentServiceUrl).build();

        Map<String, Object> response = webClient.post()
                .uri("/agent/parse")
                .bodyValue(Map.of("resume_text", resumeText))
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        log.info("Agent 1 解析完成");
        return response;
    }

    /**
     * 调用 Agent 2: JD 匹配
     */
    public Map<String, Object> matchJD(Map<String, Object> parsedResume) {
        log.info("调用 Agent 2 进行 JD 匹配");

        WebClient webClient = webClientBuilder.baseUrl(agentServiceUrl).build();

        Map<String, Object> response = webClient.post()
                .uri("/agent/match")
                .bodyValue(Map.of("parsed_resume", parsedResume))
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        log.info("Agent 2 匹配完成，分数: {}", response.get("match_score"));
        return response;
    }

    /**
     * 调用 Agent 3: 深度评估
     */
    public Map<String, Object> evaluate(Map<String, Object> parsedResume, Map<String, Object> matchResult) {
        log.info("调用 Agent 3 进行深度评估");

        WebClient webClient = webClientBuilder.baseUrl(agentServiceUrl).build();

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("parsed_resume", parsedResume);
        requestBody.put("match_result", matchResult);

        Map<String, Object> response = webClient.post()
                .uri("/agent/evaluate")
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(Map.class)
                .block();

        log.info("Agent 3 评估完成，综合得分: {}", response.get("overall_score"));
        return response;
    }
}
