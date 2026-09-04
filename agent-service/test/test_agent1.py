# 读取测试简历
import json

import requests

with open('../../data/resumes/candidate_001_张伟_high.md', 'r', encoding='utf-8') as f:
    resume_text = f.read()

# 调用 Agent 1（绕过代理）
print("开始")
response = requests.post(
    'http://localhost:5000/agent/parse',
    json={'resume_text': resume_text},
    proxies={'http': None, 'https': None}
)

print("状态码:", response.status_code)
print("响应文本:", response.text)
if response.status_code == 200:
    print("响应 JSON:", json.dumps(response.json(), indent=2, ensure_ascii=False))