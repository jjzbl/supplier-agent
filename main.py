import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import Literal
from fastapi import FastAPI, HTTPException
from google.genai import errors
from pydantic import BaseModel, ValidationError

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_CANDIDATES = ["abc", "xyz"]
app = FastAPI()

class SupplierInfo(BaseModel):
    name: str
    years_established: int      # 成立年限
    registered_capital: float   # 注册资本（万元）
    business_scope: str         # 经营范围


class ScoreResult(BaseModel):
    name: str
    score: int
    risk_level: str
    reasons: list[str]

class ScopeJudgment(BaseModel):
    relevance: Literal["高度相关", "部分相关", "无关"]
    reason: str

def get_risk_level(score: int) -> str:
    if score >= 80:
        return "低风险"
    elif score >= 50:
        return "中风险"
    else:
        return "高风险"
    

def judge_scope(business_scope: str) -> ScopeJudgment:
    prompt = (
     "你是化工贸易公司的客商准入审核助手。"
        "请判断下面这家供应商的经营范围，与化工原料、大宗商品贸易的相关程度，"
        "relevance 只能是：高度相关、部分相关、无关 之一；reason 用一句话说明理由。\n\n"
        f"经营范围：{business_scope}"
    )

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ScopeJudgment,
                ),
            )
            return ScopeJudgment.model_validate_json(response.text)
        
        except errors.APIError as e:
            print(f"模型 {model_name} 调用失败：{e}")
        except  ValidationError as e:
            print(f"模型 {model_name} 返回格式不对：{e}")

    # 循环走完都没有 return，说明所有模型都失败了
    raise HTTPException(status_code=503, detail="AI 服务暂时不可用，请稍后重试")

@app.get("/")
def health_check():
    return {"status":"ok"}

@app.post("/score", response_model=ScoreResult)
def score_supplier(info: SupplierInfo):
    score = 0
    reasons = []

    if info.years_established >=5:
        score +=50
        reasons.append("成立满 5 年，经营相对稳定")

    else:
        score += 20
        reasons.append("成立不足 5 年，需关注经营稳定性")

    if info.registered_capital >= 1000:
        score += 50
        reasons.append("注册资本较高")
    else:
        score += 20
        reasons.append("注册资本偏低")

    risk_level = get_risk_level(score)

    return ScoreResult(
        name=info.name, score=score, risk_level=risk_level, reasons=reasons

    )

@app.post("/score_ai", response_model=ScoreResult)
def score_supplier_ai(info: SupplierInfo):
    score = 0
    reasons = []

    # TODO 1：成立年限（满 5 年 40 分；2-5 年 25 分；不足 2 年 10 分）
    #         加分，并往 reasons 里加一句理由


    if info.years_established >= 5:
        score += 40
        reasons.append("成立满 5 年，经营相对稳定（+40）")

    elif info.years_established >= 2:
        score += 25
        reasons.append("成立2-5年,需关注经营稳定性（+25）")

    else:
        score += 10
        reasons.append("成立不足2年（+10）")

    # TODO 2：注册资本（≥1000 万 30 分；100-1000 万 20 分；不足 100 万 5 分）

    if info.registered_capital >= 1000:
        score += 30
        reasons.append("注册资本较高（+30）")

    elif info.registered_capital >= 100:
        score += 20
        reasons.append("注册资本一般（+20）")

    else:
        score += 5
        reasons.append("注册资本偏低（+5）")

    judgment = judge_scope(info.business_scope)
    scope_points = {"高度相关": 30, "部分相关": 15, "无关": 0}[judgment.relevance]
    score += scope_points
    reasons.append(f"经营范围{judgment.relevance}（+{scope_points}）：{judgment.reason}")


    # TODO 3：根据 score 算出 risk_level（≥80 低风险；50-79 中风险；<50 高风险）
    risk_level = get_risk_level(score)
    return ScoreResult(name=info.name, score=score, risk_level=risk_level, reasons=reasons)
