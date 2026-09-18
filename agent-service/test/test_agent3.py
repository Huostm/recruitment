import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.resume_parser import ResumeParseAgent
from agents.jd_matcher import JDMatchAgent
from agents.evaluator import EvaluatorAgent

# 读取测试简历
resume_path = 'c:/Users/Administrator/Desktop/final_project/data/resumes/candidate_001_张伟_high.md'
with open(resume_path, 'r', encoding='utf-8') as f:
    resume_text = f.read()

print("=" * 60)
print("测试 Agent 3: 深度评估器")
print("=" * 60)

# 使用 Agent 1 解析简历
print("\n[Agent 1] 解析简历...")
parser = ResumeParseAgent()
parsed_result = parser.parse(resume_text)

if not parsed_result.get('success'):
    print(f"解析失败: {parsed_result.get('error')}")
    exit(1)

parsed_resume = parsed_result['data']
print(f"解析成功: {parsed_resume.get('name')}")

# 使用 Agent 2 进行 JD 匹配
print("\n[Agent 2] JD 匹配...")
matcher = JDMatchAgent()
match_result = matcher.match(parsed_resume)
print(f"匹配分数: {match_result['match_score']}")
print(f"  - 技能: {match_result['match_details']['skill_score']}")
print(f"  - 教育: {match_result['match_details']['education_score']}")
print(f"  - 经验: {match_result['match_details']['experience_score']}")

# 测试 Agent 3
print("\n[Agent 3] 深度评估...")
evaluator = EvaluatorAgent()
evaluation = evaluator.evaluate(parsed_resume, match_result)

print(f"\n{'='*60}")
print("评估结果")
print(f"{'='*60}")
print(f"技术深度: {evaluation['tech_depth_score']}/100")
print(f"学习能力: {evaluation['learning_ability_score']}/100")
print(f"综合得分: {evaluation['overall_score']}/100")
print(f"\n优势:")
for strength in evaluation['strengths']:
    print(f"  - {strength}")
print(f"\n劣势:")
for weakness in evaluation['weaknesses']:
    print(f"  - {weakness}")
print(f"\n推荐结论: {evaluation['recommendation']}")
print(f"推荐理由: {evaluation['reason']}")
