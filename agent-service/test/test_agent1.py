# 直接测试 Agent 1 类
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.resume_parser import ResumeParseAgent

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
resume_path = os.path.join(base_dir, 'data', 'resumes', 'candidate_001_张伟_high.md')

with open(resume_path, 'r', encoding='utf-8') as f:
    resume_text = f.read()

# 测试 Agent 1
print("开始解析简历...")
agent = ResumeParseAgent()
result = agent.parse(resume_text)

print("\n解析结果:")
print(json.dumps(result, indent=2, ensure_ascii=False))