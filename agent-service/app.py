from dotenv import load_dotenv
from flask import Flask, jsonify, request
from agents.resume_parser import ResumeParseAgent
from agents.jd_matcher import JDMatchAgent
from agents.evaluator import EvaluatorAgent

load_dotenv()
app = Flask(__name__)

# 初始化 Agents
parser_agent = ResumeParseAgent()
matcher_agent = JDMatchAgent()
evaluator_agent = EvaluatorAgent()


@app.route("/health", methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

# Agent 1：简历解析
@app.route("/agent/parse", methods=['POST'])
def parse_resume():
    data = request.json
    resume_text = data.get("resume_text")

    if not resume_text:
        return jsonify({"success": False, "message": "缺少 resume_text 参数"}), 400

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
        }), 500


# Agent 2：JD 匹配（初筛）
@app.route("/agent/match", methods=['POST'])
def match_jd():
    data = request.json
    parsed_resume = data.get("parsed_resume")

    if not parsed_resume:
        return jsonify({"success": False, "message": "缺少 parsed_resume 参数"}), 400

    try:
        result = matcher_agent.match(parsed_resume)
        return jsonify({
            "success": True,
            "data": result,
            "message": "JD 匹配完成"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"JD 匹配失败: {str(e)}"
        }), 500


# Agent 3：深度评估
@app.route("/agent/evaluate", methods=['POST'])
def evaluate():
    data = request.json
    parsed_resume = data.get("parsed_resume")
    match_result = data.get("match_result")

    if not parsed_resume:
        return jsonify({"success": False, "message": "缺少 parsed_resume 参数"}), 400

    try:
        result = evaluator_agent.evaluate(parsed_resume, match_result)
        return jsonify({
            "success": True,
            "data": result,
            "message": "深度评估完成"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"深度评估失败: {str(e)}"
        }), 500


# 完整流程：一次性完成 Agent 1 → 2 → 3
@app.route("/agent/process", methods=['POST'])
def process_resume():
    """完整简历处理流程"""
    data = request.json
    resume_text = data.get("resume_text")

    if not resume_text:
        return jsonify({"success": False, "message": "缺少 resume_text 参数"}), 400

    try:
        # Agent 1: 解析简历
        parse_result = parser_agent.parse(resume_text)
        if not parse_result['success']:
            return jsonify({
                "success": False,
                "message": f"简历解析失败: {parse_result.get('error')}",
                "stage": "parse"
            }), 500

        parsed_resume = parse_result['data']

        # Agent 2: JD 匹配（初筛）
        match_result = matcher_agent.match(parsed_resume)

        # 如果初筛不通过，直接返回
        if match_result['status'] == 'rejected':
            return jsonify({
                "success": True,
                "data": {
                    "parsed_resume": parsed_resume,
                    "match_result": match_result,
                    "evaluation": None,
                    "final_status": "rejected",
                    "message": "JD 匹配分数 <50，初筛淘汰"
                }
            })

        # Agent 3: 深度评估
        evaluation = evaluator_agent.evaluate(parsed_resume, match_result)

        return jsonify({
            "success": True,
            "data": {
                "parsed_resume": parsed_resume,
                "match_result": match_result,
                "evaluation": evaluation,
                "final_status": evaluation['status'],
                "message": "处理完成"
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"处理失败: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)