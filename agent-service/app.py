from dotenv import load_dotenv
from flask import Flask, jsonify, request
from agents.resume_parser import ResumeParseAgent

load_dotenv()
app = Flask(__name__)
parser_agent = ResumeParseAgent()

@app.route("/health",methods=['GET'])
def health_check():
    return jsonify({"status":"ok"})

# Agent 1：简历解析
@app.route("/agent/parse",methods=['POST'])
def parse_resume():
    data = request.json
    resume_text = data.get("resume_text")
    # 实现简历解析逻辑
    if not resume_text:
        return jsonify({"success":False,"data":"缺少 resume_text 参数"})

    result = parser_agent.parse(resume_text)
    if result['success']:
        return jsonify({
            "success": True,
            "data": result['data'],
            "message": "简历解析成功"
        })
    else:
        return jsonify({
            "success": False,
            "message": f"解析失败: {result.get('error', 'Unknown error')}"
        })

# Agent 2：JD 匹配
@app.route("/agent/match",methods=['POST'])
def match_jd():
    data = request.json
    # TODO:实现 JD 匹配逻辑
    return jsonify({"success":"True","data":{}})

# Agent 3：深度评估
@app.route("/agent/evaluate",methods=['POST'])
def evaluate():
    data = request.json
    # TODO:实现深度评估逻辑
    return jsonify({"success":"True","data":{}})

# Agent 4：生成邀请邮件
@app.route("/agent/generate-invitation",methods=['POST'])
def generate_invitation():
    data = request.json
    # TODO:实现邮件生成逻辑
    return jsonify({"success":"True","data":{}})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)