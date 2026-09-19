from typing import Dict, List
from services.llm_service import LLMService
from services.milvus_service import MilvusService


class JDMatchAgent:

    def __init__(self):
        self.llm_service = LLMService()
        self.milvus_service = MilvusService()
        self.threshold = 50
        self.jd_education_requirement = self._extract_jd_education_requirement()

    def match(self, parsed_resume: Dict) -> Dict:
        """执行 JD 匹配

        参数:
            parsed_resume: Agent 1 的解析结果
                {
                    "name": "张伟",
                    "education": {...},
                    "skills": {...},
                    "experience": [...]
                }

        返回:
            {
                "match_score": 73.33,
                "status": "pending",
                "match_details": {
                    "skill_score": 85,
                    "education_score": 75,
                    "experience_score": 60,
                    "matched_dimensions": 2
                },
                "top_jd_chunks": [...]
            }
        """
        try:
            # 1. 生成三个维度的文本
            skill_text = self._generate_skill_text(parsed_resume.get('skills', {}))
            education_text = self._generate_education_text(parsed_resume.get('education', {}))
            experience_text = self._generate_experience_text(parsed_resume.get('experience', []))

            # 2. 分维度检索 Milvus（技能和经验）
            skill_matches = self.milvus_service.search(skill_text, top_k=3)
            experience_matches = self.milvus_service.search(experience_text, top_k=3)

            # 3. 计算每个维度的分数（0-100）
            skill_score = self._calculate_score(skill_matches)
            education_score = self._calculate_education_score(parsed_resume.get('education', {}))
            experience_score = self._calculate_score(experience_matches)

            # 4. 计算加权平均分（技能40% + 教育20% + 经验40%）
            avg_score = round(skill_score * 0.4 + education_score * 0.2 + experience_score * 0.4, 2)

            # 5. 判断状态（简化逻辑）
            if avg_score >= self.threshold:
                status = "pass"  # 通过初筛，进入深度评估
            else:
                status = "rejected"  # 直接淘汰

            # 6. 收集所有分数 >= 70% 的 JD chunks
            all_chunks = skill_matches + experience_matches
            top_chunks = [chunk for chunk in all_chunks if chunk['score'] >= 0.7]
            # 按分数排序
            top_chunks = sorted(top_chunks, key=lambda x: x['score'], reverse=True)

            return {
                "match_score": avg_score,
                "status": status,
                "match_details": {
                    "skill_score": skill_score,
                    "education_score": education_score,
                    "experience_score": experience_score
                },
                "top_jd_chunks": top_chunks
            }

        except Exception as e:
            print(f"JD 匹配失败: {e}")
            # 失败时返回默认结果，状态设为 pass 让后续流程继续
            return {
                "match_score": 0,
                "status": "pass",
                "match_details": {
                    "skill_score": 0,
                    "education_score": 0,
                    "experience_score": 0
                },
                "top_jd_chunks": [],
                "error": str(e)
            }

    def _generate_skill_text(self, skills: Dict) -> str:
        """生成技能维度的文本"""
        parts = []
        for category, skill_list in skills.items():
            if skill_list:
                parts.append(f"{category}: {', '.join(skill_list)}")
        return " | ".join(parts) if parts else "无技能信息"

    def _generate_education_text(self, education: Dict) -> str:
        """生成教育维度的文本"""
        school = education.get('school', '')
        major = education.get('major', '')
        degree = education.get('degree', '')
        return f"{school} {major} {degree}".strip() or "无教育信息"

    def _generate_experience_text(self, experience) -> str:
        """生成经验维度的文本"""
        # 处理两种格式：直接列表 或 {"projects": [...]}
        if isinstance(experience, dict):
            projects = experience.get('projects', [])
        elif isinstance(experience, list):
            projects = experience
        else:
            return "无项目经验"

        if not projects:
            return "无项目经验"

        # 拼接所有项目的标题和描述
        parts = []
        for proj in projects:
            name = proj.get('name', proj.get('title', ''))
            desc = proj.get('description', '')
            tech = proj.get('tech_stack', [])
            if isinstance(tech, list):
                tech = ', '.join(tech)
            parts.append(f"{name}: {desc} 技术栈: {tech}")

        return " | ".join(parts)

    def _calculate_score(self, matches: List[Dict]) -> int:
        """计算维度分数

        参数:
            matches: Milvus 返回的匹配结果
                [{"id": 1, "text": "...", "score": 0.85}, ...]

        返回:
            0-100 的整数分数
        """
        if not matches:
            return 0

        # 只统计相似度 >= 0.6 的结果
        valid_matches = [m for m in matches if m['score'] >= 0.6]

        if not valid_matches:
            return 0  # 没有高质量匹配，返回 0 分

        # 取平均相似度分数
        avg_similarity = sum([m['score'] for m in valid_matches]) / len(valid_matches)
        # 转换为 0-100 分
        return int(avg_similarity * 100)

    def _extract_jd_education_requirement(self) -> Dict:
        """从 JD 中提取教育要求

        返回:
            {
                "min_degree": "本科",  # 专科/本科/硕士/博士
                "preferred_majors": ["计算机", "软件工程"]
            }
        """
        try:
            # 从 Milvus 检索所有 JD chunks
            sample_results = self.milvus_service.search("教育背景 学历要求", top_k=5)

            if not sample_results:
                return {"min_degree": "本科", "preferred_majors": []}

            # 拼接相关文本
            jd_texts = [r['text'] for r in sample_results]
            context = "\n".join(jd_texts)

            # 用 LLM 提取结构化信息
            prompt = f"""从以下 JD 文本中提取教育要求：

{context}

请严格按照以下 JSON 格式返回（只返回 JSON，不要其他内容）：
{{
    "min_degree": "专科/本科/硕士/博士之一",
    "preferred_majors": ["专业1", "专业2"]
}}

如果 JD 中说"本科及以上"，则 min_degree 为"本科"。
如果看不出明确要求，默认 min_degree 为"本科"。"""

            llm = self.llm_service.get_llm()
            response = llm.invoke(prompt)

            import json
            result = json.loads(response.content)
            print(f"提取到 JD 教育要求: {result}")
            return result

        except Exception as e:
            print(f"提取 JD 教育要求失败: {e}")
            return {"min_degree": "本科", "preferred_majors": []}

    def _calculate_education_score(self, education: Dict) -> int:
        """计算教育分数（动态匹配 JD 要求）

        参数:
            education: 教育信息
                {
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "degree": "本科"
                }

        返回:
            0-100 的整数分数
        """
        score = 0

        # 学历等级定义
        degree_levels = {
            "专科": 1,
            "本科": 2,
            "硕士": 3,
            "博士": 4
        }

        # 获取候选人学历等级
        candidate_degree = education.get('degree', '')
        candidate_level = 0
        for deg, level in degree_levels.items():
            if deg in candidate_degree:
                candidate_level = level
                break

        # 获取 JD 要求的最低学历等级
        required_degree = self.jd_education_requirement.get('min_degree', '本科')
        required_level = degree_levels.get(required_degree, 2)

        # 学历匹配（50分）
        if candidate_level == 0:
            score += 10  # 无法识别学历，给最低分
        elif candidate_level < required_level:
            score += 20  # 不满足最低要求
        elif candidate_level == required_level:
            score += 50  # 满足要求
        else:  # candidate_level > required_level
            score += 50  # 超出要求也是满足

        # 学校等级（30分）- 用 LLM 推断
        school = education.get('school', '')
        school_score = 10  # 默认分数

        if school:
            try:
                prompt = f"学校名称：{school}\n请判断这所学校的等级。只回答以下之一：985/211/双一流/普通/未知"
                llm = self.llm_service.get_llm()
                response = llm.invoke(prompt).content.strip()

                if '985' in response:
                    school_score = 30
                    print(f"LLM 推断学校 '{school}' 为 985")
                elif '211' in response or '双一流' in response:
                    school_score = 20
                    print(f"LLM 推断学校 '{school}' 为 211/双一流")
                else:
                    school_score = 10
                    print(f"LLM 推断学校 '{school}' 为普通院校")
            except Exception as e:
                print(f"LLM 推断学校等级失败: {e}")
                school_score = 10

        score += school_score

        # 专业匹配（20分）
        major = education.get('major', '')
        preferred_majors = self.jd_education_requirement.get('preferred_majors', [])

        # 如果 JD 有指定专业要求，则检查是否匹配
        if preferred_majors:
            if any(pm in major for pm in preferred_majors):
                score += 20
            else:
                score += 5  # 专业不匹配
        else:
            # JD 没有明确专业要求，给中等分
            score += 10

        return min(score, 100)