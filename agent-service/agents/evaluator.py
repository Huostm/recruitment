from typing import Dict
from services.llm_service import LLMService


class EvaluatorAgent:
    """Agent 3: 深度评估器

    基于 JD 要求深度分析候选人的综合能力：
    - 技术深度评估（项目复杂度、技术栈深度）
    - 学习能力评估（技术广度、自驱力）
    - 综合潜力评分
    """

    def __init__(self):
        self.llm_service = LLMService()

    def evaluate(self, parsed_resume: Dict, match_result: Dict) -> Dict:
        """执行深度评估

        参数:
            parsed_resume: Agent 1 的解析结果
            match_result: Agent 2 的匹配结果

        返回:
            {
                "tech_depth_score": 75,
                "learning_ability_score": 80,
                "overall_score": 77,
                "strengths": ["..."],
                "weaknesses": ["..."],
                "recommendation": "推荐/待定/不推荐",
                "reason": "...",
                "status": "approved_auto/pending/rejected_recoverable"
            }
        """
        try:
            # 1. 准备上下文
            name = parsed_resume.get('name', '候选人')
            education = parsed_resume.get('education', {})
            skills = parsed_resume.get('skills', {})
            experience = parsed_resume.get('experience', [])

            # 从 match_result 获取维度得分
            match_details = match_result.get('match_details', {})
            skill_score = match_details.get('skill_score', 0)
            education_score = match_details.get('education_score', 0)
            experience_score = match_details.get('experience_score', 0)
            overall_match = match_result.get('match_score', 0)

            # 2. 构建评估 Prompt
            prompt = self._build_evaluation_prompt(
                name, education, skills, experience,
                skill_score, education_score, experience_score, overall_match
            )

            # 3. 调用 LLM 进行评估
            llm = self.llm_service.get_llm()
            response = llm.invoke(prompt)

            # 4. 解析 LLM 返回的 JSON
            import json
            evaluation = json.loads(response.content)

            # 5. 根据综合得分确定状态
            overall_score = evaluation.get('overall_score', 0)
            if overall_score >= 70:
                status = "approved"  # 自动发送面试邀请
            elif overall_score >= 30:
                status = "pending"  # 人工审核
            else:
                status = "rejected"  # 直接拒绝

            evaluation['status'] = status
            print(f"评估完成: {name} - 综合得分 {overall_score}, 状态: {status}")
            return evaluation

        except Exception as e:
            print(f"深度评估失败: {e}")
            # 返回默认评估结果
            return {
                "tech_depth_score": 0,
                "learning_ability_score": 0,
                "overall_score": 0,
                "strengths": [],
                "weaknesses": ["评估失败"],
                "recommendation": "待定",
                "reason": f"评估过程出错: {str(e)}",
                "status": "pending",  # 评估失败时让人工审批
                "error": str(e)
            }

    def _build_evaluation_prompt(
        self, name: str, education: Dict, skills: Dict,
        experience, skill_score: int, education_score: int,
        experience_score: int, overall_match: float
    ) -> str:
        """构建评估 Prompt"""

        # 格式化教育背景
        edu_text = f"{education.get('school', '')} | {education.get('major', '')} | {education.get('degree', '')}"

        # 格式化技能
        skill_items = []
        for category, skill_list in skills.items():
            if skill_list:
                skill_items.append(f"- {category}: {', '.join(skill_list)}")
        skills_text = "\n".join(skill_items) if skill_items else "无"

        # 格式化项目经验
        if isinstance(experience, dict):
            projects = experience.get('projects', [])
        elif isinstance(experience, list):
            projects = experience
        else:
            projects = []

        exp_items = []
        for proj in projects:
            proj_name = proj.get('name', proj.get('title', ''))
            proj_desc = proj.get('description', '')
            tech_stack = proj.get('tech_stack', [])
            if isinstance(tech_stack, list):
                tech_stack = ', '.join(tech_stack)
            exp_items.append(f"- {proj_name}\n  描述: {proj_desc}\n  技术栈: {tech_stack}")
        exp_text = "\n".join(exp_items) if exp_items else "无"

        prompt = f"""你是一位资深技术面试官，正在评估一位 Agent 开发实习生候选人。

候选人信息：
姓名: {name}
教育背景: {edu_text}

技能:
{skills_text}

项目经验:
{exp_text}

JD 匹配得分（Agent 2 已完成）:
- 技能匹配: {skill_score}/100
- 教育匹配: {education_score}/100
- 经验匹配: {experience_score}/100
- 综合匹配: {overall_match}/100

岗位要求（Agent 开发实习生）:
- 熟悉 LangChain/LangGraph 框架
- 了解 Multi-Agent 系统架构
- 掌握向量数据库（Milvus/Pinecone 等）
- 熟悉 RAG 技术栈
- 有完整的 Agent 项目经验

请从以下维度深度评估候选人：

1. **技术深度** (0-100分):
   - 项目复杂度如何？
   - 技术栈掌握深度如何？
   - 是否有 Agent 相关经验？

2. **学习能力** (0-100分):
   - 技术广度如何？
   - 是否展现自驱力？
   - 是否有快速学习新技术的能力？

3. **综合评价**:
   - 优势（列出 2-3 点）
   - 劣势（列出 2-3 点）
   - 推荐结论（推荐/待定/不推荐）
   - 推荐理由（50 字以内）

请严格按照以下 JSON 格式返回（只返回 JSON，不要其他内容）：
{{
    "tech_depth_score": 75,
    "learning_ability_score": 80,
    "overall_score": 77,
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["劣势1", "劣势2"],
    "recommendation": "推荐/待定/不推荐",
    "reason": "推荐理由"
}}

评估标准：
- overall_score = (tech_depth_score + learning_ability_score) / 2
- overall_score >= 70 → 推荐
- 30 <= overall_score < 70 → 待定
- overall_score < 30 → 不推荐
"""
        return prompt
