import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.resume_parser import ResumeParseAgent
from agents.jd_matcher import JDMatchAgent

# 读取测试简历
resume_path = 'c:/Users/Administrator/Desktop/final_project/data/resumes/candidate_015_曾辉_low.md'
with open(resume_path, 'r', encoding='utf-8') as f:
    resume_text = f.read()

# 使用 Agent 1 解析简历
print("使用 Agent 1 解析简历...")
parser = ResumeParseAgent()
parsed_result = parser.parse(resume_text)

if not parsed_result.get('success'):
    print(f"解析失败: {parsed_result.get('error')}")
    exit(1)

parsed_resume = parsed_result['data']
print(f"解析成功: {parsed_resume.get('name')}\n")

# 测试 Agent 2
print("=" * 60)
print("测试 Agent 2: JD 匹配")
print("=" * 60)

agent = JDMatchAgent()
result = agent.match(parsed_resume)

print(f"\n候选人: {parsed_resume.get('name')}")
print(f"匹配分数: {result['match_score']}")
print(f"状态: {result['status']}")
print(f"\n维度分数:")
print(f"  - 技能: {result['match_details']['skill_score']}")
print(f"  - 教育: {result['match_details']['education_score']}")
print(f"  - 经验: {result['match_details']['experience_score']}")
print(f"\nTop JD chunks:")
for i, chunk in enumerate(result['top_jd_chunks'][:3], 1):
    print(f"{i}. [score={chunk['score']:.3f}] {chunk['text'][:80]}...")
