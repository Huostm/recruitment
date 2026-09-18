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
print("完整流程测试: Agent 1 → Agent 2 → Agent 3")
print("=" * 60)

# Agent 1: 解析简历
print("\n[Agent 1] 解析简历...")
parser = ResumeParseAgent()
parsed_result = parser.parse(resume_text)

if not parsed_result.get('success'):
    print(f"解析失败: {parsed_result.get('error')}")
    exit(1)

parsed_resume = parsed_result['data']
print(f"姓名: {parsed_resume.get('name')}")

# Agent 2: JD 匹配（初筛）
print("\n[Agent 2] JD 初筛...")
matcher = JDMatchAgent()
match_result = matcher.match(parsed_resume)
print(f"JD 匹配分数: {match_result['match_score']}")
print(f"  - 技能: {match_result['match_details']['skill_score']}")
print(f"  - 教育: {match_result['match_details']['education_score']}")
print(f"  - 经验: {match_result['match_details']['experience_score']}")
print(f"初筛状态: {match_result['status']}")

# 判断是否通过初筛
if match_result['status'] == 'rejected':
    print("\n[X] JD 匹配分数 <50，初筛淘汰")
    print("流程结束")
    exit(0)

print("\n[OK] JD 匹配分数 >=50，通过初筛，进入深度评估")

# Agent 3: 深度评估
print("\n[Agent 3] 深度评估...")
evaluator = EvaluatorAgent()
evaluation = evaluator.evaluate(parsed_resume, match_result)
print(f"技术深度: {evaluation['tech_depth_score']}/100")
print(f"学习能力: {evaluation['learning_ability_score']}/100")
print(f"综合得分: {evaluation['overall_score']}/100")
print(f"推荐结论: {evaluation['recommendation']}")
print(f"最终状态: {evaluation['status']}")

# 根据状态决定是否发送面试邀请
print(f"\n{'='*60}")
print("流程决策")
print(f"{'='*60}")

status = evaluation['status']
if status == "approved":
    print("[OK] 综合得分 >=70，自动通过")
    print("-> 后端将自动发送面试邀请邮件到候选人 QQ 邮箱")
    print("-> 面试链接: https://www.baidu.com")

elif status == "pending":
    print("[!] 综合得分 50-70，进入人工审核")
    print("-> HR 可以在审核界面决定是否发送面试邀请")

elif status == "rejected":
    print("[X] 综合得分 <50，直接挂掉")
    print("-> HR 可以在审核界面捞回并发送面试邀请")

print(f"\n{'='*60}")
print("流程完成")
print(f"{'='*60}")
